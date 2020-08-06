import os
from datetime import datetime

print("Start")


updateSoftwareInstallCmd = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/install.sh')
# Fix for this test script
updateSoftwareInstallCmd = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('test')[0], 'install/install.sh')
print("updateSoftwareInstallCmd: {}".format(updateSoftwareInstallCmd))


updateSoftwareLogFile = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/log/update_{}.log'.format(datetime.now().strftime("%Y%m%d%H%M%S")))
# Fix for this test script
updateSoftwareLogFile = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('test')[0], 'install/log/update_{}.log'.format(datetime.now().strftime("%Y%m%d%H%M%S")))
print("updateSoftwareLogFile: {}".format(updateSoftwareLogFile))

# os.system("nohup sudo -b bash -c 'sleep 2; /home/pi/Oppleo/install/install.sh' &>/dev/null")
print("nohup sudo -u pi -b bash -c 'sleep 2; {} &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
# update script kills Oppleo, and also os.system or os.popen processes. Spawn new process that will survive the Oppleo kill

os.popen("nohup sudo -u pi -b bash -c 'sleep 2; {} &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))

print("Done!")
