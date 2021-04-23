import threading
import os
from os import path
import ntpath
import subprocess
from datetime import datetime, timedelta, time
from time import sleep
import logging
import re
import json
from shutil import which

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

from nl.oppleo.utils.formatFilesize import formatFilesize
from nl.oppleo.utils.SMBClient import SMBClient
from nl.oppleo.services.PushMessage import PushMessage
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil


# A function that returns the length of the value:
def sortBackups(file:dict) -> int:
    try:
        return int(datetime.strptime(file['filename'][7:26], '%Y-%m-%d_%H.%M.%S').timestamp())
    except Exception as e:
        logger = logging.getLogger('nl.oppleo.utils.sortBackups')
        logger.debug('sortBackups() Exception {}'.format(str(e)))
    return 0


"""
    Create sql dump backup
    List backups
    Remove backups from local filesystem
    Create config backup (ini file)
    Copy backup to Samba share
    Copy backup to AFP share (?)

"""


"""
 Instantiate an BackupUtil() object. This will be a Singleton
 
"""

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BackupUtil(object, metaclass=Singleton):

    stop_event = None
    monitorThread = None
    singleBackupThread = None
    backupInProgress = False
    lock = None

    # Check once per minute. Sleep is 0.1s to respond to interrupts
    __CHECK_INTERVAL = 60

    __DBTYPE_POSTGRESS__ = 0

    __SYSTEMSINIPATH__ = 'src/nl/oppleo/config/'
    __SYSTEMSINIFILENAME__ = 'oppleo'
    __SYSTEMSINIFILEEXT__ = 'ini'              # .ini

    __LIQUIBASEPROPPATH__ = 'db/'
    __LIQUIBASEPROPFILENAME__ = 'liquibase'
    __LIQUIBASEPROPFILEEXT__ = 'properties'    # .properties

    __SERVICEPATH__ = 'install/'
    __SERVICEFILENAME__ = 'Oppleo'
    __SERVICEFILEEXT__ = 'service'             # .service

    __INSTALLLOGPATH__ = 'install/log/'
    __INSTALLLOGFILENAME__ = 'update_'
    __INSTALLLOGFILEEXT__ = 'log'               # .log

    __dbtype__ = __DBTYPE_POSTGRESS__


    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.utils.BackupUtil')
        self.oppleoConfig = OppleoConfig()
        self.oppleoSystemConfig = OppleoSystemConfig()
        self.monitorThread = None
        self.singleBackupThread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()


    """
        Create temporary directory in backup directory
            Create a db backup dump
            copy /src/nl/oppleo/config/oppleo.ini
            copy /db/liquibase.properties
            zip /db/sql directory
        Zip all in one backup file
        Remove temporary folder

    """


    """
        Start the monitor thread, which keeps an eye out if a backup is due, and 
        automatically creates one 
    """
    def startBackupMonitorThread(self) -> bool:
        self.logger.debug('startBackupMonitorThread() - BackupMonitorThread')
        # self.thread = self.oppleoConfig.appSocketIO.start_background_task(self.monitorEnergyDevicesLoop)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        if self.monitorThread is not None and self.monitorThread.is_alive():
            # Thread already running, don't start another one 
            return False
        self.stop_event.clear()
        self.monitorThread = threading.Thread(target=self.monitorBackupDueStatusLoop, name='BackupMonitorThread')
        self.monitorThread.start()
        return True


    def stopBackupMonitorThread(self) -> bool:
        self.logger.debug('stopBackupMonitorThread() - BackupMonitorThread')
        if self.monitorThread is None or not self.monitorThread.is_alive():
            # Thread not running, don't need to stop it 
            return False
        self.stop_event.set()
        # wait for thread to stop
        while self.monitorThread.is_alive():
            pass
        return True


    """
        Start the monitor thread, either as single run or as loop
    """
    def startSingleBackupThread(self) -> bool:
        self.logger.debug('startSingleBackupThread() - SingleBackupThread')
        # self.thread = self.oppleoConfig.appSocketIO.start_background_task(self.monitorEnergyDevicesLoop)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        if self.singleBackupThread is not None and self.singleBackupThread.is_alive():
            # Thread already running, don't start another one 
            return False
        self.singleBackupThread = threading.Thread(target=self.createBackup, name='SingleBackupThread')
        self.singleBackupThread.start()

        return True


    def monitorBackupDueStatusLoop(self):
        self.__CHECK_INTERVAL
        timer = 0
        while not self.stop_event.is_set():
            if timer > self.__CHECK_INTERVAL:
                timer = 0
                # Check if backup is due
                if self.isBackupDue():
                    self.logger.debug('monitorBackupDueStatusLoop() - backup due!')
                    self.createBackup()
            timer += (1 * .1)
            # Backup is minute precise. Sleep is interruptable by other threads, but sleeping 60 seconds before checking 
            # if stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
            sleep(.1)


    def createBackup(self):
        if self.backupInProgress:
            # Skip this backup request, already running one
            self.logger.debug('createBackup() - backup already active. Additional backup aborted.')
            WebSocketUtil.emit(
                    wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                    event='backup_request_ignored', 
                    id=self.oppleoConfig.chargerName,
                    data={"reason" : 'Backup in progress' },
                    namespace='/backup',
                    public=False
                )
            return
        self.backupInProgress = True

        try:
            startTime = datetime.now()
            wsData = { "started"     : startTime.strftime('%Y-%m-%d %H:%M.%S') }

            filesize = 0
            # Announce
            WebSocketUtil.emit(
                    wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                    event='backup_started', 
                    id=self.oppleoConfig.chargerName,
                    data=wsData,
                    namespace='/backup',
                    public=False
                )
            localBackup = self.createLocalBackup(start_time=startTime)
            self.logger.debug('createBackup() - local backup created (success={})'.format(localBackup['success']))

            remoteBackup = None
            if localBackup['success']:
                wsData.update({'localBackupSuccess': True, 'filename': localBackup['filename']})
                # Purge excess backups
                self.purgeLocalBackups(n=self.oppleoConfig.backupLocalHistory)
                if self.oppleoConfig.osBackupEnabled:
                    self.logger.debug('createBackup() - offsite backup enabled')
                    # Create offsite backup
                    if (self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB):
                        self.logger.debug('createBackup() - remoteBackup type {}'.format(self.oppleoConfig.OS_BACKUP_TYPE_SMB_STR))
                        wsData.update({'osBackupType': self.oppleoConfig.OS_BACKUP_TYPE_SMB})
                        remoteBackup = self.__storeBackupToSmbShare__(filename=localBackup['filename'], localpath=localBackup['path'])
                        if remoteBackup['success']:
                            # Purge excess SMB backups
                            self.__purgeBackupSmbShare__(n=self.oppleoConfig.osBackupHistory)
                        self.logger.debug('createBackup() - offsite backup created (success={})'.format(remoteBackup['success']))
                        wsData.update({'osBackupSuccess': remoteBackup['success']})
                        if not remoteBackup['success']:
                            wsData.update({'osBackupFailedReason': remoteBackup['reason']})
                wsData.update({'osBackupEnabled': self.oppleoConfig.osBackupEnabled})

                # Get the fileszie
                try: 
                    filesize = os.path.getsize(os.path.join(localBackup['path'], localBackup['filename']))
                    wsData.update({'filesize': filesize})
                except OSError as ose:
                    pass

            timeCompleted = datetime.now()
            wsData.update({'completed': timeCompleted.strftime('%Y-%m-%d %H:%M.%S')})

            wsEvent = 'backup_failed'
            # Announce
            if (localBackup['success'] and 
                    (not self.oppleoConfig.osBackupEnabled or 
                            (self.oppleoConfig.osBackupEnabled and remoteBackup['success'])
                    )
                ):
                # Full success
                self.oppleoConfig.backupSuccessTimestamp = startTime
                wsEvent = 'backup_completed'

            WebSocketUtil.emit(
                        wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                        event=wsEvent, 
                        id=self.oppleoConfig.chargerName,
                        data=wsData,
                        namespace='/backup',
                        public=False
                    )

            pushMsg = ("Local backup {}{} {}."
                    .format(
                        ('(' + formatFilesize(filesize) + ')') if localBackup['success'] else '',
                        ' completed' if localBackup['success'] else 'failed',
                        timeCompleted.strftime('%A %-d %B %Y, %H:%Mu')
                    )
                )
            pushMsg += (" {}"
                    .format(
                        "(Offsite backup not enabled)" if not self.oppleoConfig.osBackupEnabled else (
                            "Offsite backup (SMB) distribution to //{}/{}{} {}".format(
                                self.oppleoConfig.smbBackupServerNameOrIPAddress, 
                                self.oppleoConfig.smbBackupServiceName, 
                                self.oppleoConfig.smbBackupRemotePath,
                                'completed.' if remoteBackup['success'] else 'failed!'
                            ) if self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB else (
                                "Offsite backup enabled but type ({}) not supported.".format(self.oppleoConfig.osBackupType)
                            )
                        )
                    )
                )

            PushMessage.sendMessage(
                    "Backup {}"
                        .format('completed' if wsEvent == 'backup_completed' else 'failed'), 
                    pushMsg
                )

        except Exception as e:
            self.logger.debug('createBackup() - Exception {}'.format(str(e)))
        # Signal end of backup
        self.backupInProgress = False
        self.logger.debug('createBackup() - Done')


    def createLocalBackup(self, start_time:datetime=None):
        # 0. Make timestamp if not provided
        self.logger.debug('createLocalBackup()')
        if (start_time == None):
            start_time = datetime.now()
        files = []
        # 1. Create temporary directory in the backup directory
        tmp_dir, backup_dir = self.__createTemporaryDirectory__(start_time)
        self.logger.debug('createLocalBackup() tmp_dir={} backup_dir={}'.format(tmp_dir, backup_dir))

        # 2. Create a db backup dump in the temporary directory
        res = self.backupDatabase(start_time, tmp_dir)
        self.logger.debug('createLocalBackup() backupDatabase success={}'.format(res['success']))
        if not res['success']:
            # Backup failed
            return { 'success': False, 'filename': None, 'reason': res['reason'] }
        files.append(res['filename'])
        # 3. Copy /src/nl/oppleo/config/oppleo.ini
        files.append(self.__copySystemsIniFile__(start_time, tmp_dir))
        self.logger.debug('createLocalBackup() __copySystemsIniFile__')
        # 4. Copy /db/liquibase.properties
        files.append(self.__copyLiquibasePropertiesFile__(start_time, tmp_dir))
        self.logger.debug('createLocalBackup() __copyLiquibasePropertiesFile__')
        # 5. copy the service file (can be generated, history on platform)
        # install/Oppleo.service
        files.append(self.__copyServiceConfigFile__(start_time, tmp_dir))
        self.logger.debug('createLocalBackup() __copyServiceConfigFile__')
        # 5. copy the install log files (history on platform)
        files.append(self.__zipInstallLogFiles__(start_time, tmp_dir))
        self.logger.debug('createLocalBackup() __zipInstallLogFiles__')
        # 6. Zip temporary directory in one backup file
        backup_file = self.__zipBackupFile__(start_time, backup_dir, tmp_dir, files)
        self.logger.debug('createLocalBackup() __zipBackupFile__')
        # 7. Remove temporary folder
        self.__removeTemporaryDirectory__(tmp_dir, files)
        self.logger.debug('createLocalBackup() __removeTemporaryDirectory__')

        return { 'success': True, 'filename': backup_file, 'path': backup_dir }



    def __createTemporaryDirectory__(self, now: datetime):
        self.logger.debug('__createTemporaryDirectory__()')
        backup_dir = self.oppleoConfig.localBackupDirectory
        if not backup_dir.endswith(os.path.sep):
            backup_dir += os.path.sep

        tmp_directory = backup_dir + 'tmp_' + now.strftime('%Y-%m-%d_%H.%M.%S')

        if not os.path.exists(tmp_directory):
            os.makedirs(tmp_directory)

        if not tmp_directory.endswith(os.path.sep):
            tmp_directory += os.path.sep

        self.logger.debug('__createTemporaryDirectory__() tmp_directory={} backup_dir={}'.format(tmp_directory, backup_dir))
        return tmp_directory, backup_dir

    def __copySystemsIniFile__(self, now: datetime, tmp_dir):
        ini_source_filename = self.__SYSTEMSINIFILENAME__ + '.' + self.__SYSTEMSINIFILEEXT__ 
        ini_target_filename = self.__SYSTEMSINIFILENAME__ + '_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '.' + self.__SYSTEMSINIFILEEXT__ 

        ini_source_path = os.path.join(self.oppleoConfig.oppleoRootDirectory, 
                                       self.__SYSTEMSINIPATH__,            
                                       ini_source_filename
                                      )
        ini_target_path = os.path.join(tmp_dir, 
                                       ini_target_filename
                                      )
        try:
            self.logger.debug('__copySystemsIniFile__() cp {} {}'.format(ini_source_path, ini_target_path))
            os.system('cp ' + ini_source_path + ' ' + ini_target_path)
        except Exception as e:
            self.logger.debug('__copySystemsIniFile__() cp Exception {}'.format(str(e)))

        return ini_target_filename


    def __copyLiquibasePropertiesFile__(self, now: datetime, tmp_dir):
        liqbase_source_filename = self.__LIQUIBASEPROPFILENAME__ + '.' + self.__LIQUIBASEPROPFILEEXT__ 
        liqbase_target_filename = self.__LIQUIBASEPROPFILENAME__ + '_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '.' + self.__LIQUIBASEPROPFILEEXT__ 

        liqbase_source_path = os.path.join(self.oppleoConfig.oppleoRootDirectory, 
                                       self.__LIQUIBASEPROPPATH__,            
                                       liqbase_source_filename
                                      )
        liqbase_target_path = os.path.join(tmp_dir, 
                                       liqbase_target_filename
                                      )
        try:
            self.logger.debug('__copyLiquibasePropertiesFile__() cp {} {}'.format(liqbase_source_path, liqbase_target_path))
            os.system('cp ' + liqbase_source_path + ' ' + liqbase_target_path)
        except Exception as e:
            self.logger.debug('__copyLiquibasePropertiesFile__() cp Exception {}'.format(str(e)))

        return liqbase_target_filename



    def __copyServiceConfigFile__(self, now: datetime, tmp_dir):
        service_source_filename = self.__SERVICEFILENAME__ + '.' + self.__SERVICEFILEEXT__ 
        service_target_filename = self.__SERVICEFILENAME__ + '_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '.' + self.__SERVICEFILEEXT__ 

        service_source_path = os.path.join(self.oppleoConfig.oppleoRootDirectory, 
                                       self.__SERVICEPATH__,            
                                       service_source_filename
                                      )
        service_target_path = os.path.join(tmp_dir, 
                                       service_target_filename
                                      )
        try:
            self.logger.debug('__copyServiceConfigFile__() cp {} {}'.format(service_source_path, service_target_path))
            os.system('cp ' + service_source_path + ' ' + service_target_path)
        except Exception as e:
            self.logger.debug('__copyServiceConfigFile__() cp Exception {}'.format(str(e)))

        return service_target_filename

    """
        zip 
            -j   junk (don't record) directory names
    """
    def __zipInstallLogFiles__(self, now:datetime, tmp_dir:str):
        install_log_source_filename = self.__INSTALLLOGFILENAME__ + '*' + '.' + self.__INSTALLLOGFILEEXT__ 
        install_log_target_filename = self.__INSTALLLOGFILENAME__ + self.__INSTALLLOGFILEEXT__ + '_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '.zip'

        install_log_source_path = os.path.join(self.oppleoConfig.oppleoRootDirectory, 
                                       self.__INSTALLLOGPATH__,            
                                       install_log_source_filename
                                      )
        install_log_target_path = os.path.join(tmp_dir, 
                                       install_log_target_filename
                                      )
        try:
            self.logger.debug('__zipInstallLogFiles__() zip -j {} {}'.format(install_log_target_path, install_log_source_path))
            os.system('zip -j ' + install_log_target_path + ' ' + install_log_source_path)
            # zip /Users/laeme498/Projects/Oppleo/backup/tmp_2021-02-02_13.28.48/update.333.log /Users/laeme498/Projects/Oppleo/install/log/update_*.log
        except Exception as e:
            self.logger.debug('__zipInstallLogFiles__() zip Exception {}'.format(str(e)))

        return install_log_target_filename



    """
        zip 
            -j   junk (don't record) directory names
    """
    def __zipBackupFile__(self, now:datetime, backup_dir:str, tmp_dir:str, files:list):
        zipFilename = 'backup_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '_' + self.oppleoConfig.chargerName + '.zip'
        filePlusPath = os.path.join(backup_dir, zipFilename)
        try:
            self.logger.debug('__zipBackupFile__() zip -j ' + filePlusPath + ' ' + ' '.join(map((tmp_dir+'{0}').format, files)))
            os.system('zip -j ' + filePlusPath + ' ' + ' '.join(map((tmp_dir+'{0}').format, files)))
        except Exception as e:
            self.logger.debug('__zipBackupFile__() cp Exception {}'.format(str(e)))

        return zipFilename



    def __removeTemporaryDirectory__(self, tmp_dir:str, files:list):
        for file in files:
            try:
                filename = os.path.join(tmp_dir, file )
                self.logger.debug('__removeTemporaryDirectory__() rm {}'.format(filename))
                os.system('rm ' + filename)
            except Exception as e:
                self.logger.debug('__removeTemporaryDirectory__() rm Exception {}'.format(str(e)))

        try:
            self.logger.debug('__removeTemporaryDirectory__() rmdir {}'.format(tmp_dir))
            os.system('rmdir ' + tmp_dir)
        except Exception as e:
            self.logger.debug('__removeTemporaryDirectory__() rmdir Exception {}'.format(str(e)))


    """
        Returns if the path exists and is a directory
    """
    def __backupDirectoryExists__(self) -> bool:

        backupPath = self.oppleoConfig.localBackupDirectory
        return path.exists(backupPath) and path.isdir(backupPath)

    """
        Returns if the path exists and is a directory
    """
    def __createBackupDirectory__(self) -> None:

        directory = self.oppleoConfig.localBackupDirectory

        if not os.path.exists(directory):
            os.makedirs(directory)


    def backupDatabase(self, now, dir_name) -> dict:

        if self.__dbtype__ == self.__DBTYPE_POSTGRESS__:
            return self.backupDatabase_Postgres(now, dir_name)
        # default
        return { 'type': 'none', 'filename': None, 'success': False, 'reason': 'No supported database type' }

    """
        Takes some time (~10s over LAN on 1y of data)
        -> create a threat for it
    """
    def backupDatabase_Postgres(self, now, dir_name) -> dict:
        
        filename = 'postgres_' + now.strftime('%Y-%m-%d_%H.%M.%S') + '.pg_dump'

        cmd = 'pg_dump'
        if not self.__cmd_exists__(cmd):
            return { 'type': 'postgres', 'filename': None, 'success': False, 'reason': 'No postgres backup cmd available' }
        cmd = self.__cmd_which__(cmd)

        if not dir_name.endswith(os.path.sep):
            dir_name += os.path.sep

        try:
            os.system(cmd + ' ' + self.oppleoSystemConfig.DATABASE_URL + " -Fc > " + dir_name + filename)
        except Exception as e:
            return { 'type': 'postgres', 'filename': filename, 'success': False, 'reason': str(e) }

        return { 'type': 'postgres', 'filename': filename, 'success': True }


    """
        Capture stdout (returns byte literal): 
            x = subprocess.check_output(['whoami'])
        Capture proces exit code 0 means success:
            os.system() returns the (encoded) process exit value. 
    """
    def __cmd_exists__(self, cmd) -> bool:
        self.logger.debug('__cmd_exists__() command: {}'.format(cmd))

        return which(cmd) is not None


    """
        Returns the full path of a command if found on the path
    """
    def __cmd_which__(self, cmd):
        self.logger.debug('__cmd_which__() which {}'.format(cmd))

        return which(cmd)


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def listLocalBackups(self, directory:str=None):

        if directory is None:
            directory = self.oppleoConfig.localBackupDirectory
        files = []
        for filename in os.listdir(directory):
            if re.match('^backup_[0-9-_.]{19}_'+self.oppleoConfig.chargerName+r'\.zip$', filename):
                filesize = None
                try: 
                    filesize = os.path.getsize(os.path.join(directory, filename))
                except OSError as ose:
                    pass
                files.append({ 'filename': filename, 'filesize': filesize, 'timestamp': filename[7:26].replace('_', ' ') })

        files.sort(key=sortBackups)

        return { 'directory': directory, 'files': files }


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def purgeLocalBackups(self, n:int=99):
        self.logger.debug('purgeLocalBackups() n={}'.format(n))
        if n >= 99:
            self.logger.debug('purgeLocalBackups() no purge')
            return

        localBackups = self.listLocalBackups()
        # note: the list is sorted
        purgelist = localBackups['files'][0:(-1*n)] 
        self.logger.debug('purgeLocalBackups() purging {} of {} backups'.format(str(len(purgelist)), str(len(localBackups['files']))))

        for file in purgelist:
            filename = os.path.join(localBackups['directory'], file['filename'])
            os.remove(filename)

        WebSocketUtil.emit(
                    wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                    event='local_backup_purged',
                    id=self.oppleoConfig.chargerName,
                    data=localBackups['files'][0:(-1*n)],
                    namespace='/backup',
                    public=False
                )



    """
        Removes a local backup
    """
    def removeLocalBackup(self, filename:str=None):
        if filename is None:
            return { 'result': False, 'found': False, 'filename': '', 'reason': 'No filename given' }
        localBackups = self.listLocalBackups()
        localBackupFilteredList = [entry for entry in localBackups['files'] 
                                      if entry['filename'] == filename
                                  ]
        if len(localBackupFilteredList) != 1:
            return { 'result': False, 'found': False, 'reason': 'File not found', 'filename': filename }
        try:
            os.remove(os.path.join(localBackups['directory'], localBackupFilteredList[0]['filename']))
            return { 'result': True, 'found': True, 'filename': filename, 'filesize': localBackupFilteredList[0]['filesize'], 'timestamp': localBackupFilteredList[0]['timestamp'] }
        except IsADirectoryError as iad:
            return { 'result': False, 'found': True, 'filename': filename, 'reason': 'Is a directory' }
        except Exception as e:
            self.logger.debug('removeLocalBackup() Exception {}'.format(str(e)))

        return { 'result': False, 'found': True, 'filename': filename, 'reason': 'Unknown error' }


    """
        Removes an offsite backup
    """
    def removeOffsiteBackup(self, osPath:str=None, filename:str=None):
        if filename is None:
            return { 'result': False, 'found': False, 'filename': '', 'reason': 'No filename given' }

        if self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB:
            smbBackups = self.listSMBBackups()
            if not smbBackups['success']:
                return { 'result': False, 'found': False, 'filename': filename, 'reason': smbBackups['reason'] }

            smbBackupFilteredList = [entry for entry in smbBackups['files'] 
                                        if entry['filename'] == filename
                                  ]
            if len(smbBackupFilteredList) != 1:
                return { 'result': False, 'found': False, 'reason': 'File not found', 'filename': filename }
            try:
                smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                                    username=self.oppleoConfig.smbBackupUsername, 
                                    password=self.oppleoConfig.smbBackupPassword,
                                    service_name=self.oppleoConfig.smbBackupServiceName, 
                                    )
                conSuccess, conDetails = smb_client.connect()
                if not conSuccess:
                    return { 'result': False, 'found': True, 'filename': filename, 
                             'reason': 'Not resolved' if not conDetails['resolved'] else 'Connection refused' if conDetails['connectionRefused'] else 'Unknown' }
                deleteResult = smb_client.deleteFiles(remote_path=osPath if osPath is not None else self.oppleoConfig.smbBackupRemotePath,
                                                      files=[filename])
                smb_client.close()
                if deleteResult['success']:
                    return { 'result': True, 'found': True, 'filename': filename }
                else:
                    return { 'result': False, 'found': True, 'filename': filename, 'reason': deleteResult['success'] }
            except Exception as e:
                self.logger.debug('removeOffsiteBackup() Exception {}'.format(str(e)))
                return { 'result': False, 'found': True, 'filename': filename, 'reason': str(e)  }

            return { 'result': False, 'found': True, 'filename': filename, 'reason': 'Unknown' }

        return { 'result': False, 
                 'found': False, 
                 'filename': filename, 
                 'reason': 'Offsite backup type ({}) not supported'.format(self.oppleoConfig.osBackupType) 
               }


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def listOffsiteBackups(self, directory:str=None):

        if self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB:
            result = self.listSMBBackups()
            data = { 'success': result['success'] }
            if result['success']:
                data.update({ 'directory'   : result['directory'],
                              'files'       : result['files']
                            })
            else:
                data.update({ 'reason' : result['reason'] })
            return data

        return { 'success': False, 
                 'reason': 'Unsupported offsite backup type ({})'
                    .format(self.oppleoConfig.osBackupType)
               }





    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def listSMBBackups(self, smbPath:str=None, serverOrIP:str=None, username:str=None, password:str=None, 
                           serviceName:str=None):

        smb_client = SMBClient(serverOrIP=serverOrIP if serverOrIP is not None else self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=username if username is not None else self.oppleoConfig.smbBackupUsername, 
                               password=password if password is not None else self.oppleoConfig.smbBackupPassword,
                               service_name=serviceName if serviceName is not None else self.oppleoConfig.smbBackupServiceName, 
                               )
        smbfilelist = None
        try:
            smb_client.connect()
            smbfilelist = smb_client.list(smbPath=smbPath if smbPath is not None else self.oppleoConfig.smbBackupRemotePath)
            smb_client.close()
        except Exception as e:
            self.logger.debug('listSMBBackups() Exception {}'.format(str(e)))
            return { 'success': False, 
                     'reason': str(e)
                   }
        files = []
        for smbf in smbfilelist:
            if re.match('^backup_[0-9-_.]{19}_'+self.oppleoConfig.chargerName+r'\.zip$', smbf.filename):
                files.append({ 'filename'   : smbf.filename,
                               'filesize'   : smbf.file_size,
                               'timestamp'  : smbf.filename[7:26].replace('_', ' ')
                            })

        files.sort(key=sortBackups)

        return { 'success': True, 
                 'directory': smbPath if smbPath is not None else self.oppleoConfig.smbBackupRemotePath, 
                 'files': files 
               }


    """
        Returns the list of files and directories in the directory path
    """
    def listSMBFilesAndDirectories(self, smbPath:str='/', hideDirectories:bool=False, hideFiles:bool=False,
                                   serverOrIP:str=None, username:str=None, password:str=None, serviceName:str=None):

        smb_client = SMBClient(serverOrIP=serverOrIP if serverOrIP is not None else self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=username if username is not None else self.oppleoConfig.smbBackupUsername, 
                               password=password if password is not None else self.oppleoConfig.smbBackupPassword,
                               service_name=serviceName if serviceName is not None else self.oppleoConfig.smbBackupServiceName, 
                               )

        validConnection, connectionDetails = smb_client.connect()
        connectionDetails['validConnection'] = validConnection
        connectionDetails['smbPath'] = smbPath
        if not validConnection:
            return [], connectionDetails
# TODO catch invalid path in errror            
        smbFileAndDirectoryList = smb_client.list(smbPath=smbPath)
        smb_client.close()

        filesAndOrDirectories = []
        for smbf in smbFileAndDirectoryList:
            if smbf.filename not in ['.', '..']:
                if hideDirectories or hideFiles:
                    if (not hideDirectories or not smbf.isDirectory) and (not hideFiles or smbf.isDirectory):
                        filesAndOrDirectories.append(smbf.filename)
                else:
                    filesAndOrDirectories.append({ 'name': smbf.filename, 'isDirectory': smbf.isDirectory })

        if hideDirectories or hideFiles:
            filesAndOrDirectories.sort()
        else:
            filesAndOrDirectories = sorted(filesAndOrDirectories, key = lambda i: i['name'])

        return filesAndOrDirectories, connectionDetails



    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def listSMBShares(self, serverOrIP:str=None, username:str=None, password:str=None):

        smb_client = SMBClient(serverOrIP=serverOrIP if serverOrIP is not None else self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=username if username is not None else self.oppleoConfig.smbBackupUsername, 
                               password=password if password is not None else self.oppleoConfig.smbBackupPassword
                               )

        smbsharelist = None
        validConnection, connectionDetails = smb_client.connect()
        connectionDetails['validConnection'] = validConnection
        if not validConnection:
            return [], connectionDetails
        smbsharelist = smb_client.listShares()
        smb_client.close()

        sharelist = []
        for smbshare in smbsharelist:
            sharelist.append(smbshare.name)

        sharelist.sort()

        return sharelist, connectionDetails


    """
        Returns True if the user can connect
    """
    def validateSMBConnection(self) -> bool:

        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               service_name=self.oppleoConfig.smbBackupServiceName, 
                               )
        if not smb_client.connect()[0]:
            return False
        smb_client.close()
        return True

    """
        Validate Offsite Backup
    """
    def validOffsiteBackup(self):

        if self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB:
            files, connectionDetails = self.listSMBFilesAndDirectories(smbPath=self.oppleoConfig.smbBackupRemotePath)
            if connectionDetails['validConnection']:
                return True

        return False


    def validateSMBAccount(self, serverOrIP:str=None, username:str=None, password:str=None):
        smb_client = SMBClient(serverOrIP=serverOrIP, username=username, password=password)
        return smb_client.connect()


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def __storeBackupToSmbShare__(self, filename:str=None, localpath:str='/') -> dict:
        
        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               service_name=self.oppleoConfig.smbBackupServiceName, 
                               )

        smb_client.connect()
        response = smb_client.upload(remote_path=self.oppleoConfig.smbBackupRemotePath, local_path=localpath, files=[filename])
        smb_client.close()

        return response


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def __purgeBackupSmbShare__(self, n:int=99):
        self.logger.debug('__purgeBackupSmbShare__() n={}'.format(n))
        if n >= 99:
            self.logger.debug('__purgeBackupSmbShare__() no purge')
            return
        
        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               service_name=self.oppleoConfig.smbBackupServiceName, 
                               )

        smb_client.connect()

        smbBackups = self.listSMBBackups()
        if not smbBackups['success']:
            self.logger.debug('__purgeBackupSmbShare__() no purge, could not get file list - {}'.format(smbBackups['reason']))
            return
        # Sorted and filtered - now limit and get the filenames       
        purgelist = []
        for file in smbBackups['files'][0:(-1*n)]:
            purgelist.append(file['filename'])
        self.logger.debug('__purgeBackupSmbShare__() purging {} of {} backups'.format(str(len(purgelist)), str(len(smbBackups['files']))))
        result = smb_client.deleteFiles(service_name=self.oppleoConfig.smbBackupServiceName,
                                        remote_path=smbBackups['directory'],
                                        files=purgelist
                                       )
        smb_client.close()
        # Send message to front end
        WebSocketUtil.emit(
                    wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                    event='os_backup_purged',
                    id=self.oppleoConfig.chargerName,
                    data=smbBackups['files'][0:(-1*n)],
                    namespace='/backup',
                    public=False
                )
        return result


    """
        Helper function to set or reset a specific calendar day
        -- calendar days are offset by 1 (1st is index 0)
    """
    def setBackupCalDay(self, calday:int=-1, enable:bool=False):
        calDayList = json.loads(self.oppleoConfig.backupIntervalCalday)
        calDayList[calday] = enable
        self.oppleoConfig.backupIntervalCalday = json.dumps(calDayList)

    """
        Helper function to set or reset a specific weekday
        -- weekday, 0=Sunday, 1=Monday, ...
    """
    def setBackupWeekDay(self, weekday:int=-1, enable:bool=False):
        weekDayList = json.loads(self.oppleoConfig.backupIntervalWeekday)
        weekDayList[weekday] = enable
        self.oppleoConfig.backupIntervalWeekday = json.dumps(weekDayList)

    def isBackupDue(self) -> bool:
        lastBackup = self.oppleoConfig.backupSuccessTimestamp
        self.logger.debug('isBackupDue() - lastBackup: {}'.format(str(lastBackup)))
        now = datetime.now()
        self.logger.debug('isBackupDue() - now: {}'.format(str(now)))

        """
            check backup type: Weekday or Calendar day
        """

        if self.oppleoConfig.backupInterval == self.oppleoConfig.BACKUP_INTERVAL_WEEKDAY:
            self.logger.debug('isBackupDue() - backupInterval == BACKUP_INTERVAL_WEEKDAY')
            """
                --> Weekday
                    Determine due date by first enabled day since now (iterate through weekDayList from todays day), set due time,
                    and verify if last backup was prior or after due day/time.
            """
            weekDayList = json.loads(self.oppleoConfig.backupIntervalWeekday)
            # Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
            weekDayToday = now.weekday()
    
            # Find the first required backup time, by looking back in enabled days
            daysPast = 8
            for i in range(7):
                # +1 to convert from 0=Monday to 0=Sunday
                # -i to go backwards through the week (7 days = range(7))
                daysPast = i if weekDayList[(weekDayToday+1-i)%7] and daysPast == 8 else daysPast

            self.logger.debug('isBackupDue() - daysPast={}, '.format(daysPast))

            due = ((datetime.now() - timedelta(days=daysPast))
                    .replace(hour=self.oppleoConfig.backupTimeOfDay.hour, 
                             minute=self.oppleoConfig.backupTimeOfDay.minute,
                             second=0, 
                             microsecond=0
                             )
                  )
            self.logger.debug('isBackupDue() - due: {}, '.format(due))

            self.logger.debug('isBackupDue() - due? : {}, '.format((daysPast != 8 and lastBackup < due and now > due)))
            # Backup due? (daysPast=8 indicates no active days)
            return daysPast != 8 and lastBackup < due and now > due


        if self.oppleoConfig.backupInterval == self.oppleoConfig.BACKUP_INTERVAL_CALDAY:
            """
                --> Calendar day
                    If todays date is enabled and time has passed, or any calendar day since success was enabled -> Go
                    
            """
            calDayList = json.loads(self.oppleoConfig.backupIntervalCalday)
            # Return the day of the month as an integer, where the first is 1.
            calDayToday = now.day
    
            # Find the first required backup time, by looking back in enabled days
            daysPast = 32
            for i in range(31):
                # +1 to convert from 0=Monday to 0=Sunday
                # -i to go backwards through the month (31 days = range(31))
                daysPast = i if calDayList[(calDayToday+1-i)%31] and daysPast == 32 else daysPast

            due = ((datetime.now() - timedelta(days=daysPast))
                    .replace(hour=self.oppleoConfig.backupTimeOfDay.hour, 
                             minute=self.oppleoConfig.backupTimeOfDay.minute,
                             second=0, 
                             microsecond=0
                             )
                  )

            # Backup due? (daysPast=32 indicates no active days)
            return daysPast != 32 and lastBackup < due


        """
            None of the above, no backup then
        """

        return False
