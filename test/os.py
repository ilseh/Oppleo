import re
import subprocess

def systemCtlStatus():
    result = subprocess.run(["systemctl status Oppleo.service"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    ctl = {}
    ctl['status'] = "-"
    ctl['pid'] = "-"
    ctl['mem'] = "-"

    # Get the process status
    try:
        for line in result.stdout.split('\n'):
            if re.search('Active:', line):
                ctl['status'] = line.split("Active:",1)[1].strip()
                break
    except:
        pass

    # Get the process pid
    try:
        for line in result.stdout.split('\n'):
            if re.search('Main PID:', line):
                ctl['pid'] = line.split("Main PID:",1)[1].split("(",1)[0].strip()
                break
    except:
        pass

    # Get the memory usage
    try:
        for line in result.stdout.split('\n'):
            if re.search('Memory:', line):
                ctl['mem'] = line.split("Memory:",1)[1].strip()
                break
    except:
        pass
    
    return ctl

print(systemCtlStatus())
