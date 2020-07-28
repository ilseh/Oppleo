import os
from datetime import datetime
from typing import Optional

class GitUtil(object):
    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastBranchGitDate(branch="") -> Optional[datetime]:
        # Wed Jul 22 15:40:45 2020 +0200\n
        try:
            return datetime.strptime(os.popen('git log -1 --format=%cd {}'.format(branch)).read().rstrip(), '%a %b %d %H:%M:%S %Y %z')
        except (RuntimeError, TypeError, ValueError, NameError) as e:
            return None

    @staticmethod
    def lastBranchGitDateStr(branch="") -> Optional[str]:
        d = GitUtil.lastBranchGitDate(branch=branch)
        return (str(d.strftime("%d/%m/%Y, %H:%M:%S")) if (d is not None) else "Onbekend")

    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastRemoteMasterGitDate() -> Optional[datetime]:
        return GitUtil.lastBranchGitDate(branch="origin/master")

    @staticmethod
    def lastRemoteMasterGitDateStr() -> Optional[str]:
        return GitUtil.lastBranchGitDateStr(branch="origin/master")

    @staticmethod
    def gitUpdateAvailable() -> Optional[bool]:
        localGitDate = GitUtil.lastBranchGitDate() 
        remoteGitDate = GitUtil.lastRemoteMasterGitDate()
        return (localGitDate is not None and remoteGitDate is not None and \
                localGitDate < remoteGitDate)

    # Updates the git status with the remote server
    @staticmethod
    def gitRemoteUpdate() -> None:
        try:
            os.popen('git remote update')
        except (RuntimeError, TypeError, ValueError, NameError) as e:
            pass

