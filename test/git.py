import os
from datetime import datetime

# Wed Jul 22 15:40:45 2020 +0200\n
try:
    # rstrip strips the newline
    localGitDate = datetime.strptime(os.popen('git log -1 --format=%cd').read().rstrip(), '%a %b %d %H:%M:%S %Y %z')
except (RuntimeError, TypeError, ValueError, NameError) as e:
    localGitDate = None
try:
    remoteGitDate = datetime.strptime(os.popen('git log -1 --format=%cd origin/master').read().rstrip(), '%a %b %d %H:%M:%S %Y %z')
except (RuntimeError, TypeError, ValueError, NameError) as e:
    remoteGitDate = None

print("Current git status: {} ".format(localGitDate))
print("Git repository: {} ".format(remoteGitDate))

if localGitDate == None:
    print("Cannot read local git status...")
if remoteGitDate == None:
    print("Cannot read Github date...")
if localGitDate != None and remoteGitDate != None and localGitDate > remoteGitDate:
    print("We are ahead! Need to push changes")
if  localGitDate != None and remoteGitDate != None and localGitDate == remoteGitDate:
    print("Up-to-date :)")
if  localGitDate != None and remoteGitDate != None and localGitDate < remoteGitDate:
    print("Update available")
