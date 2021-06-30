import os
import logging
import re
from datetime import datetime
from nl.oppleo.utils.GitUtil import GitUtil
from nl.oppleo.config.OppleoConfig import oppleoConfig


"""
 Instantiate an OppleoConfig() object. This will be a Singleton
 
"""

class Version():
    major:int = 0
    minor:int = 0
    build:int = 0

    def __init__(self, version:str='0.0.0'):
        self.__logger = logging.getLogger('nl.oppleo.config.Version')
        if version is None:
            return
        keys = version.split('.')
        self.major = int(keys[0])
        self.minor = int(keys[1]) if len(keys) > 0 else 0
        self.build = int(keys[2]) if len(keys) > 1 else 0

    def isNewer(self, version=None):
        if version is None:
            return True
        return ( self.major > version.major or
                 ( self.major == version.major and self.minor > version.minor ) or
                 ( self.major == version.major and self.minor == version.minor and self.build > version.build )
               )

    def __str__(self):
        return "{}.{}.{}".format(self.major, self.minor, self.build)


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ChangeLog():
    __logger = None
    __FILENAME = 'changelog.txt'
    __changelog = {}
    __currentVersion = None
    __currentVersionDate = None

    en_US = 0
    nl_NL = 1
    __lang_max = 1
    __lang_default = 1

    """ MONTH OF YEAR IS ONE BASED - DATETIME MONTH IS ONE BASED """
    month = [ ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ],
              ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December' ] ]


    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.config.ChangeLog')

        fileContent = self.__readChangeLogFile__()
        parsedChangeLog = self.parse(changeLogText=fileContent)
        self.__currentVersion, self.__currentVersionDate = self.getMostRecentVersion(parsedChangeLog)
        self.__changelog = parsedChangeLog


    def __readChangeLogFile__(self) -> str:
        global oppleoConfig

        localDocDirectory = oppleoConfig.localDocDirectory
        if not localDocDirectory.endswith(os.path.sep):
            localDocDirectory += os.path.sep

        changeLogFile = open(localDocDirectory + self.__FILENAME, "r")
        changeLogText = ''
        for line in changeLogFile:
            changeLogText += line

        changeLogFile.close()

        return changeLogText        


    def parse(self, changeLogText:str=None):
        if changeLogText is None:
            return None

        changeLog = {}
        versionNumber = None
        versionDate = None
        section = None
        changeLogLines = changeLogText.split('\n')
        for line in changeLogLines:
            # Remove the waiste
            line = line.strip()
            # Skip empty lines
            if line == '':
                continue
            # New version section i.e. Version 1.2.1   2021-04-22
            if line.lower().startswith('version'):
                # Tabs to space
                line = line.replace('\t', ' ')
                # Multiple spaces to single space
                line = re.sub('\s+',' ',line).strip()
                lineSections = line.split(' ')
                versionNumber   = lineSections[1].strip()
                versionDate     = lineSections[2].strip()
                changeLog[versionNumber] = {}
                changeLog[versionNumber]['version'] = Version(versionNumber)
                changeLog[versionNumber]['date'] = versionDate
                section = None
                continue
            if line.lower().startswith('added'):
                section = 'Added'
                changeLog[versionNumber][section] = []
                continue
            if line.lower().startswith('fixed'):
                section = 'Fixed'
                changeLog[versionNumber][section] = []
                continue
            
            if versionNumber is not None and section is not None:
                # Remove bullets
                if line.startswith('-'):
                    line = line[1:].strip()
                changeLog[versionNumber][section].append(line)

        return changeLog


    def getMostRecentVersion(self, changeLogObj:dict=None):
        if changeLogObj is None:
            return (None, None)

        versionNumber   = None
        versionDate     = None
        for changeLogEntry in changeLogObj:

            if changeLogObj[changeLogEntry]['version'].isNewer(versionNumber):
                versionNumber = changeLogObj[changeLogEntry]['version']
                versionDate = self.__dateStrToDate__(changeLogObj[changeLogEntry]['date'])

        return (versionNumber, versionDate)


    @property
    def currentVersion(self):
        return self.__currentVersion

    @property
    def currentVersionDate(self):
        return self.__currentVersionDate

    @property
    def versionHistory(self):
        return self.__changelog

    def __dateStrToDate__(self, dateStr):
        if len(dateStr) != 10:
            return None
        dateSpl = dateStr.split('-')
        if len(dateSpl) != 3:
            return None
        try:
            return datetime(int(dateSpl[0]), int(dateSpl[1]), int(dateSpl[2]))
        except Exception as e:
            return None


    def versionDateStr(self, lang:int=0, versionDate:datetime=None):
        if lang > self.__lang_max:
            lang = self.__lang_default
        if versionDate is None:
            return "Date unknown"
        try:
            # datetime month is 1-based, the array 0-based
            return "{} {} {}".format(versionDate.day, self.month[lang][versionDate.month-1], versionDate.year)
        except Exception as e:
            return "Date unknown"

    def currentVersionDateStr(self, lang:int=0):
        return self.versionDateStr(lang=lang, versionDate=self.__currentVersionDate)

    def branches(self):
        (activeBranch, branches) = GitUtil.gitBranches()
        return branches
        
    def activeBranch(self):
        (activeBranch, branches) = GitUtil.gitBranches()
        return activeBranch

    def all(self, lang:int=0):
        (activeBranch, branchNames) = GitUtil.gitBranches()
        branches = {}
        for branchName in branchNames:
            changeLogText = GitUtil.getChangeLogForBranch(branchName)
            if changeLogText is None:
                # Timeout or similar, return what we have untill now
                return branches
            parsedChangeLog = changeLog.parse(changeLogText=changeLogText)
            (versionNumber, versionDate) = changeLog.getMostRecentVersion(changeLogObj=parsedChangeLog)
            branches[branchName] = {
                'branch': branchName, 
                'version': str(versionNumber) if versionNumber is not None else '0.0.0', 
                'date': changeLog.versionDateStr(lang=lang, versionDate=versionDate) if versionDate is not None else 'null', 
                }
        return branches



changeLog = ChangeLog()

