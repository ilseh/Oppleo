import threading
import os
from os import path
import ntpath
import subprocess
from datetime import datetime, timedelta, time
import logging
import re
import json


from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.utils.GenericUtil import GenericUtil

from nl.oppleo.utils.SMBClient import SMBClient
from nl.oppleo.services.PushMessage import PushMessage
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil


# A function that returns the length of the value:
def sortBackups(file:dict) -> int:
    try:
        return int(datetime.strptime(file['filename'][7:26], '%Y-%m-%d_%H.%M.%S').timestamp())
    except Exception as e:
        pass
    return 0


"""
    Create sql dump backup
    List backups
    Remove backups from local filesystem
    Create config backup (ini file)
    Copy backup to Samba share
    Copy backup to AFP share (?)

"""




class BackupUtil:

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
        self.logger = logging.getLogger('nl.oppleo.services.BackupUtil')
        self.oppleoConfig = OppleoConfig()
        self.oppleoSystemConfig = OppleoSystemConfig()
        if GenericUtil.isProd():
            self.logger.debug('Production environment')
        else:
            self.logger.debug('Not production environment')



    """
        Create temporary directory in backup directory
            Create a db backup dump
            copy /src/nl/oppleo/config/oppleo.ini
            copy /db/liquibase.properties
            zip /db/sql directory
        Zip all in one backup file
        Remove temporary folder

    """
    def startCreateBackupTask(self):
        self.logger.debug(f'{datetime.now()} - Launching backup background task...')
        self.thread = self.oppleoConfig.appSocketIO.start_background_task(self.createBackup)


    def createBackup(self):
        startTime = datetime.now()
        # Announce
        WebSocketUtil.emit(
                wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                event='backup_started', 
                id=self.oppleoConfig.chargerName,
                data={
                    "started"     : startTime.strftime('%Y-%m-%d %H:%M.%S')
                },
                namespace='/backup',
                public=False
            )
        backup_file = self.createLocalBackup(start_time=startTime)

        if self.oppleoConfig.osBackupEnabled:
            # Create offsite backup
            if (self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB):
                self.__storeBackupToSmbShare__(filename=backup_file)

        timeCompleted = datetime.now()

        # Get the fileszie
        filesize = 0
        try: 
            filesize = os.path.getsize(backup_file)
        except OSError as ose:
            pass

        # Announce
        WebSocketUtil.emit(
                wsEmitQueue=self.oppleoConfig.wsEmitQueue,
                event='backup_completed', 
                id=self.oppleoConfig.chargerName,
                data={
                    "started"     : startTime.strftime('%Y-%m-%d %H:%M.%S'),
                    "completed"   : timeCompleted.strftime('%Y-%m-%d %H:%M.%S'),
                    "filename"    : ntpath.basename(backup_file),
                    "filesize"    : filesize
                },
                namespace='/backup',
                public=False
            )

        PushMessage.sendMessage(
            "Backup completed", 
            "Backup completed at {} {}"
            .format(
                timeCompleted.strftime('%Y-%m-%d %H:%M'),
                "(offsite backup not enabled)" if not self.oppleoConfig.osBackupEnabled else (
                    "(Offsite copy to SMB //{}/{}/{})".format(
                        self.oppleoConfig.smbBackupServerNameOrIPAddress, 
                        self.oppleoConfig.smbBackupServiceName, 
                        self.oppleoConfig.smbBackupSharePath
                        ) if self.oppleoConfig.osBackupType == self.oppleoConfig.OS_BACKUP_TYPE_SMB else (
                            "(offsite backup type not supported"
                        )
                    )
                )
            )


    def createLocalBackup(self, start_time:datetime=None):
        # 0. Make timestamp if not provided
        if (start_time == None):
            start_time = datetime.now()
        files = []
        # 1. Create temporary directory in the backup directory
        tmp_dir, backup_dir = self.__createTemporaryDirectory(start_time)
        # 2. Create a db backup dump in the temporary directory
        # --- files.append(self.backupDatabase(now, tmp_dir))
        # 3. Copy /src/nl/oppleo/config/oppleo.ini
        files.append(self.__copySystemsIniFile(start_time, tmp_dir))
        # 4. Copy /db/liquibase.properties
        files.append(self.__copyLiquibasePropertiesFile(start_time, tmp_dir))
        # 5. copy the service file (can be generated, history on platform)
        # install/Oppleo.service
        files.append(self.__copyServiceConfigFile(start_time, tmp_dir))
        # 5. copy the install log files (history on platform)
        files.append(self.__zipInstallLogFiles(start_time, tmp_dir))
        # 6. Zip temporary directory in one backup file
        backup_file = self.__zipBackupFile(start_time, backup_dir, tmp_dir, files)
        # 7. Remove temporary folder
        self.__removeTemporaryDirectory(tmp_dir, files)

        return backup_file


    def __createTemporaryDirectory(self, now: datetime):
        backup_dir = self.oppleoConfig.localBackupDirectory
        if not backup_dir.endswith(os.path.sep):
            backup_dir += os.path.sep

        tmp_directory = backup_dir + 'tmp_' + now.strftime('%Y-%m-%d_%H.%M.%S')

        if not os.path.exists(tmp_directory):
            os.makedirs(tmp_directory)

        if not tmp_directory.endswith(os.path.sep):
            tmp_directory += os.path.sep

        return tmp_directory, backup_dir

    def __copySystemsIniFile(self, now: datetime, tmp_dir):
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
            print('cp ' + ini_source_path + ' ' + ini_target_path)
            os.system('cp ' + ini_source_path + ' ' + ini_target_path)
        except Exception as e:
            pass
        return ini_target_filename


    def __copyLiquibasePropertiesFile(self, now: datetime, tmp_dir):
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
            print('cp ' + liqbase_source_path + ' ' + liqbase_target_path)
            os.system('cp ' + liqbase_source_path + ' ' + liqbase_target_path)
        except Exception as e:
            pass
        return liqbase_target_filename



    def __copyServiceConfigFile(self, now: datetime, tmp_dir):
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
            print('cp ' + service_source_path + ' ' + service_target_path)
            os.system('cp ' + service_source_path + ' ' + service_target_path)
        except Exception as e:
            pass
        return service_target_filename

    """
        zip 
            -j   junk (don't record) directory names
    """
    def __zipInstallLogFiles(self, now:datetime, tmp_dir:str):
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
            print('zip -j ' + install_log_target_path + ' ' + install_log_source_path)
            os.system('zip -j ' + install_log_target_path + ' ' + install_log_source_path)

            # zip /Users/laeme498/Projects/Oppleo/backup/tmp_2021-02-02_13.28.48/update.333.log /Users/laeme498/Projects/Oppleo/install/log/update_*.log

        except Exception as e:
            pass
        return install_log_target_filename



    """
        zip 
            -j   junk (don't record) directory names
    """
    def __zipBackupFile(self, now:datetime, backup_dir:str, tmp_dir:str, files:list):

        backup_filename = os.path.join(backup_dir, 
                                       'backup_' + 
                                       now.strftime('%Y-%m-%d_%H.%M.%S') + 
                                       '_' +
                                       self.oppleoConfig.chargerName +
                                       '.zip'
                                    )

        try:
            print('zip -j ' + backup_filename + ' ' + ' '.join(map((tmp_dir+'{0}').format, files)))
            os.system('zip -j ' + backup_filename + ' ' + ' '.join(map((tmp_dir+'{0}').format, files)))
        except Exception as e:
            pass
        return backup_filename



    def __removeTemporaryDirectory(self, tmp_dir:str, files:list):
        for file in files:
            try:
                filename = os.path.join(tmp_dir, file )
                print('rm ' + filename)
                os.system('rm ' + filename)
            except Exception as e:
                pass
        try:
            print('rmdir ' + tmp_dir)
            os.system('rmdir ' + tmp_dir)
        except Exception as e:
            pass




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


    def backupDatabase(self, now, dir_name):

        if self.__dbtype__ == self.__DBTYPE_POSTGRESS__:
            return self.backupDatabase_Postgres(now, dir_name)
        # default
        return

    """
        Takes some time (~10s over LAN on 1y of data)
        -> create a threat for it
    """
    def backupDatabase_Postgres(self, now, dir_name):
        
        filename = 'postgres_' + now.strftime('%Y-%m-%d_%H.%M.%S')

        cmd = 'pg_dump'
        if not self.__cmd_exists__(cmd):
            return
        cmd = self.__cmd_which__(cmd)

        if not dir_name.endswith(os.path.sep):
            dir_name += os.path.sep

        print(cmd + ' ' + self.oppleoSystemConfig.DATABASE_URL + " -Fc > " + dir_name + filename + '.pg_dump')
        try:
            os.system(cmd + ' ' + self.oppleoSystemConfig.DATABASE_URL + " -Fc > " + dir_name + filename + '.pg_dump')
        except Exception as e:
            pass


    """
        Capture stdout (returns byte literal): 
            x = subprocess.check_output(['whoami'])
        Capture proces exit code 0 means success:
            os.system() returns the (encoded) process exit value. 
    """
    def __cmd_exists__(self, cmd) -> bool:
        
        try:
            # Returns 0 if found, 1 if not present
            return int(subprocess.check_output('command -v ' + cmd + ' &> /dev/null; echo "$?"', shell=True)) == 0
        except Exception as e:
            pass
        return False


    """
        Returns the full path of a command if found on the path
    """
    def __cmd_which__(self, cmd):

        try:
            full_path = subprocess.check_output('which ' + cmd, shell=True).decode("utf-8").strip()

            return (None if len(full_path) == 0 else full_path)
        except Exception as e:
            pass
        return None

    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def listLocalBackups(self, directory:str=None):

        if directory is None:
            directory = self.oppleoConfig.localBackupDirectory
        files = []
        for filename in os.listdir(directory):
            if re.match('^backup_[0-9-_.]{19}_'+self.oppleoConfig.chargerName+'\.zip$', filename):
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
    def purgeLocalBackups(self, n:int=5):

        directory, files = self.listLocalBackups()
        # TODO return is dict now
        # note: the list is sorted
        purgelist = files[0:(-1*n)] 
        for file in purgelist:
            filename = os.path.join(directory, file)
            os.remove(filename)

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
            pass
        return { 'result': False, 'found': True, 'filename': filename, 'reason': 'Unknown error' }


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

        smb_client.connect()
        smbfilelist = smb_client.list(smbPath if smbPath is not None else self.oppleoConfig.smbBackupSharePath)
        smb_client.close()

        files = []
        for smbf in smbfilelist:
            if re.match('^backup_[0-9-_.]{19}_'+self.oppleoConfig.chargerName+'\.zip$', smbf.filename):
                files.append(smbf.filename)

        files.sort(key=sortBackups)

        return self.oppleoConfig.smbBackupSharePath, files


    """
        Returns the list of files and directories in the directory path
    """
    def listSMBFilesAndDirectories_OLD(self, smbPath:str='/', hideDirectories:bool=False, hideFiles:bool=False):

        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               service_name=self.oppleoConfig.smbBackupServiceName, 
                               )

        smb_client.connect()
        smbFileAndDirectoryList = smb_client.list(smbPath)
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

        return smbPath, filesAndOrDirectories

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


    def validateSMBAccount(self, serverOrIP:str=None, username:str=None, password:str=None):
        smb_client = SMBClient(serverOrIP=serverOrIP, username=username, password=password)
        return smb_client.connect()


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def __storeBackupToSmbShare__(self, filename:str):
        
        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerNameOrIPAddress,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               service_name=self.oppleoConfig.smbBackupServiceName, 
                               )

        smb_client.connect()
        response = smb_client.upload([os.path.join(self.oppleoConfig.smbBackupSharePath, filename)])
        smb_client.close()

        PushMessage.sendMessage(
            "Offsite Backup failed", 
            "Could not write backup file {} to SMB //{}/{}/{}!"
            .format(
                 filename, 
                 self.oppleoConfig.smbBackupServerNameOrIPAddress, 
                 self.oppleoConfig.smbBackupServiceName, 
                 self.oppleoConfig.smbBackupSharePath
                )
            )

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
        lastBackup = None
        try:
            lastBackup = datetime.fromtimestamp(
                int(self.oppleoConfig.backupSuccessTimestamp)
            )
        except Exception as e:
            return True

        now = datetime.now()

        """
            check backup type: Weekday or Calendar day
        """

        if self.oppleoConfig.backupInterval == self.oppleoConfig.BACKUP_INTERVAL_WEEKDAY:
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
                # +i to go through the week (7 days)
                daysPast = i if weekDayList[(weekDayToday+1+i)%7] and daysPast == 8 else daysPast

            due = datetime.now() - timedelta(days=daysPast)
            due.replace(hour=self.oppleoConfig.backupTimeOfDay[0,2], minute=self.oppleoConfig.backupTimeOfDay[3,2])

            # Backup due? (daysPast=8 indicates no active days)
            return daysPast != 8 and lastBackup < due


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
                # +i to go through the week (7 days)
                daysPast = i if calDayList[(calDayToday+1+i)%31] and daysPast == 32 else daysPast

            due = datetime.now() - timedelta(days=daysPast)
            due.replace(hour=self.oppleoConfig.backupTimeOfDay[0,2], minute=self.oppleoConfig.backupTimeOfDay[3,2])

            # Backup due? (daysPast=32 indicates no active days)
            return daysPast != 32 and lastBackup < due





            pass

        """
            None of the above, no backup then
        """

        return False
