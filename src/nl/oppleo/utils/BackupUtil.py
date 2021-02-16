import threading
import os
from os import path
import subprocess
from datetime import datetime
import logging
import re


from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.utils.GenericUtil import GenericUtil

from nl.oppleo.utils.SMBClient import SMBClient


# A function that returns the length of the value:
def sortBackups(filename:str) -> int:
    try:
        return int(datetime.strptime(filename[7:26], '%Y-%m-%d_%H.%M.%S').timestamp())
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

    __backupDirectory__ = None
    __DBTYPE_POSTGRESS__ = 0
    __DEFAULTDIRNAME__ = 'backup'

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
        self.backupDirectory = self.__getBackupDirectory__()



    """
        Create temporary directory in backup directory
            Create a db backup dump
            copy /src/nl/oppleo/config/oppleo.ini
            copy /db/liquibase.properties
            zip /db/sql directory
        Zip all in one backup file
        Remove temporary folder

    """
    def createBackup(self):
        # 0. Make timestamp
        now = datetime.now()
        files = []
        # 1. Create temporary directory in the backup directory
        tmp_dir, backup_dir = self.__createTemporaryDirectory(now)
        # 2. Create a db backup dump in the temporary directory
        # --- files.append(self.backupDatabase(now, tmp_dir))
        # 3. Copy /src/nl/oppleo/config/oppleo.ini
        files.append(self.__copySystemsIniFile(now, tmp_dir))
        # 4. Copy /db/liquibase.properties
        files.append(self.__copyLiquibasePropertiesFile(now, tmp_dir))
        # 5. copy the service file (can be generated, history on platform)
        # install/Oppleo.service
        files.append(self.__copyServiceConfigFile(now, tmp_dir))
        # 5. copy the install log files (history on platform)
        files.append(self.__zipInstallLogFiles(now, tmp_dir))
        # 6. Zip temporary directory in one backup file
        backup_file = self.__zipBackupFile(now, backup_dir, tmp_dir, files)
        # 7. Remove temporary folder
        self.__removeTemporaryDirectory(tmp_dir, files)

        return backup_file


    def __createTemporaryDirectory(self, now: datetime):
        backup_dir = self.__getBackupDirectory__()
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

        ini_source_path = os.path.join(self.__getOppleoRootDirectory__(), 
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

        liqbase_source_path = os.path.join(self.__getOppleoRootDirectory__(), 
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

        service_source_path = os.path.join(self.__getOppleoRootDirectory__(), 
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

        install_log_source_path = os.path.join(self.__getOppleoRootDirectory__(), 
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
        returns the absolute path to the backup folder
    """
    def __getBackupDirectory__(self) -> str:
        return os.path.join(self.__getOppleoRootDirectory__(), self.__DEFAULTDIRNAME__)

    """
        returns the absolute path to the backup folder
    """
    def __getOppleoRootDirectory__(self) -> str:

        if self.__backupDirectory__ is None:
            print(os.path.realpath("."))
            return os.path.realpath(".")
        return ""


    """
        Returns if the path exists and is a directory
    """
    def __backupDirectoryExists__(self) -> bool:

        backupPath = self.__getBackupDirectory__()
        return path.exists(backupPath) and path.isdir(backupPath)

    """
        Returns if the path exists and is a directory
    """
    def __createBackupDirectory__(self) -> None:

        directory = self.__getBackupDirectory__()

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

        """
        dir_name = self.__getBackupDirectory__()
        if not self.__backupDirectoryExists__():
            self.__createBackupDirectory__()
        """

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
    def listLocalBackups(self):

        directory = self.__getBackupDirectory__()
        files = []
        for f in os.listdir(directory):
            if re.match('^backup_[0-9-_.]{19}_'+self.oppleoConfig.chargerName+'\.zip$', f):
                files.append(f)

        files.sort(key=sortBackups)

        return directory, files


    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def purgeLocalBackups(self, n:int=5):

        directory, files = self.listLocalBackups()
        # note: the list is sorted
        purgelist = files[0:(-1*n)] 
        for file in purgelist:
            filename = os.path.join(directory, file)
            os.remove(filename)

    """
        Returns the list of files in the backup directory, ignoring sub directories
    """
    def __listSMBBackups__(self):

        smb_client = SMBClient(serverOrIP=self.oppleoConfig.smbBackupServerOrIP,
                               username=self.oppleoConfig.smbBackupUsername, 
                               password=self.oppleoConfig.smbBackupPassword, 
                               share_name=self.oppleoConfig.smbBackupShareName
                               )
        smb_client.connect()
        smbfilelist = smb_client.list(self.oppleoConfig.smbBackupSharePath)
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



