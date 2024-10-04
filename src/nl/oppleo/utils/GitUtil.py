import os
from git import Repo, Git, GitCommandError    # GitPython
from datetime import datetime
from typing import Optional
import requests
import logging

class GitUtil(object):
    GIT_OPPLEO_CHANGELOG_URL = 'https://raw.githubusercontent.com/ilseh/Oppleo/{branch}/doc/changelog.txt'
    DEFAULT_BRANCH = "master"
    HTTP_TIMEOUT = 5    # 30

    HTTP_200_OK = 200
    HTTP_401_UNAUTHORIZED = 401
    HTTP_408_REQUEST_TIMEOUT = 408

    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastBranchGitDate(branch:str="master", remote:bool=False) -> Optional[datetime]:
        # Wed Jul 22 15:40:45 2020 +0200\n
        if not isinstance(branch, str):
            return None
        try:
            if remote and not branch.lower().startswith('origin') and '/' not in branch:
                branch = 'origin/' + branch

            # Interprete repository
            git = Git(GitUtil.gitRepoLocation())
            dateStr = git.log('-n', 1, '--pretty=%cd', branch)
            return datetime.strptime(dateStr, '%a %b %d %H:%M:%S %Y %z')

        except (RuntimeError, TypeError, ValueError, NameError, GitCommandError) as e:
            return None

    @staticmethod
    def lastBranchGitDateStr(branch:str="master", remote:bool=False) -> Optional[str]:
        d = GitUtil.lastBranchGitDate(branch=branch, remote=remote)
        return (str(d.strftime("%d/%m/%Y, %H:%M:%S")) if (d is not None) else "Onbekend")

    # Returns a datetime object of the latest Git refresh
    @staticmethod
    def lastRemoteMasterGitDate() -> Optional[datetime]:
        return GitUtil.lastBranchGitDate(branch="master", remote=True)

    @staticmethod
    def lastRemoteMasterGitDateStr() -> Optional[str]:
        return GitUtil.lastBranchGitDateStr(branch="master", remote=True)

    @staticmethod
    def gitUpdateAvailable(branch:str="master") -> Optional[bool]:
        localGitDate = GitUtil.lastBranchGitDate(branch=branch, remote=False) 
        remoteGitDate = GitUtil.lastBranchGitDate(branch=branch, remote=True)
        return (localGitDate is not None and remoteGitDate is not None and \
                localGitDate < remoteGitDate)

    # Updates the git status with the remote server
    @staticmethod
    def gitRemoteUpdate() -> None:
        try:

            # Interprete repository
            git = Git(GitUtil.gitRepoLocation())
            # Update remote data
            git.fetch()

            # outcome = os.system('git remote update')
        except (RuntimeError, TypeError, ValueError, NameError) as e:
            pass

   # Updates the git status with the remote server
    @staticmethod
    def gitBranches():
        activeBranch = None
        branches = []

        # Interprete repository
        repo = Repo(GitUtil.gitRepoLocation())
        activeBranch = repo.active_branch.name
        for branch in repo.branches:
            branches.append( branch.name )

        return (activeBranch, branches)


    # Get the changelog file from github for the branch
    @staticmethod
    def getChangeLogForBranch(branch:str="master"):

        _logger = logging.getLogger('nl.oppleo.util.GitUtil')
        _logger.debug('getChangeLogForBranch')

        url = GitUtil.GIT_OPPLEO_CHANGELOG_URL.replace('{branch}', branch)
        _logger.debug('url: {}'.format(url))
        try:
            r = requests.get(
                url=url,
                timeout=GitUtil.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            _logger.debug('ConnectTimeout: {}'.format(ct))
            return None
        except requests.ReadTimeout as rt:
            _logger.debug('ReadTimeout: {}'.format(rt))
            return None
        if r.status_code != GitUtil.HTTP_200_OK:
            _logger.debug('status_code: {}'.format(r.status_code))
            return None

        _logger.debug('text: {}'.format(r.text))
        return r.text

   # Updates the git status with the remote server
    @staticmethod
    def gitRepoLocation():

        # Current Working Directory
        repoLoc = os.getcwd().rstrip(os.sep)

        # Remove /src if present
        if repoLoc.lower().endswith(os.sep+'src'):
            repoLoc = repoLoc[:repoLoc.rfind(os.sep)]

        return repoLoc

