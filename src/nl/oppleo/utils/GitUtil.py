import os
from datetime import datetime
from typing import Optional
import requests

class GitUtil(object):
    GIT_OPPLEO_CHANGELOG_URL = 'https://raw.githubusercontent.com/ilseh/Oppleo/{branch}/doc/changelog.txt'
    DEFAULT_BRANCH = "master"
    HTTP_TIMEOUT = 30

    HTTP_200_OK = 200
    HTTP_401_UNAUTHORIZED = 401
    HTTP_408_REQUEST_TIMEOUT = 408

    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastBranchGitDate(branch:str="master") -> Optional[datetime]:
        # Wed Jul 22 15:40:45 2020 +0200\n
        try:
            return datetime.strptime(os.popen('git log -1 --format=%cd {}'.format(branch)).read().rstrip(), '%a %b %d %H:%M:%S %Y %z')
        except (RuntimeError, TypeError, ValueError, NameError) as e:
            return None

    @staticmethod
    def lastBranchGitDateStr(branch:str="master") -> Optional[str]:
        d = GitUtil.lastBranchGitDate(branch=branch)
        return (str(d.strftime("%d/%m/%Y, %H:%M:%S")) if (d is not None) else "Onbekend")

    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastRemoteMasterGitDate(branch:str="master") -> Optional[datetime]:
        return GitUtil.lastBranchGitDate(branch=branch)

    @staticmethod
    def lastRemoteMasterGitDateStr(branch:str="master") -> Optional[str]:
        return GitUtil.lastBranchGitDateStr(branch=branch)

    @staticmethod
    def gitUpdateAvailable(branch:str="master") -> Optional[bool]:
        localGitDate = GitUtil.lastBranchGitDate(branch=branch) 
        remoteGitDate = GitUtil.lastRemoteMasterGitDate(branch=branch)
        return (localGitDate is not None and remoteGitDate is not None and \
                localGitDate < remoteGitDate)

    # Updates the git status with the remote server
    @staticmethod
    def gitRemoteUpdate() -> None:
        try:
            outcome = os.system('git remote update')
        except (RuntimeError, TypeError, ValueError, NameError) as e:
            pass

   # Updates the git status with the remote server
    @staticmethod
    def gitBranches():
        activeBranch = None
        branches = []
        try:
            branchLines = os.popen('git branch').read().rstrip().split('\n')
            for branch in branchLines:
                if branch.startswith('*'):
                    branch = branch[1:].strip()
                    activeBranch = branch
                branches.append(branch.strip())
        except (RuntimeError, TypeError, ValueError, NameError, Exception) as e:
            pass
        return (activeBranch, branches)


    # Get the changelog file from github for the branch
    @staticmethod
    def getChangeLogForBranch(branch:str="master"):
        url = GitUtil.GIT_OPPLEO_CHANGELOG_URL.replace('{branch}', branch)
        try:
            r = requests.get(
                url=url,
                timeout=GitUtil.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            return None
        except requests.ReadTimeout as rt:
            return None
        if r.status_code != GitUtil.HTTP_200_OK:
            return None

        return r.text

