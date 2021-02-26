from nl.oppleo.utils.BackupUtil import BackupUtil
from nl.oppleo.config.OppleoConfig import OppleoConfig
from datetime import datetime, timedelta, time
import json

b = BackupUtil()
oppleoConfig = OppleoConfig()

# Monday = 0, Sunday = 6
datetime_weekday = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']


oppleoConfig.backupTimeOfDay = time(hour=12, minute=10, second=0, microsecond=0)
#                                     zo     ma    di    wo    do     vr    za
oppleoConfig.backupIntervalWeekday = '[false, false, false, false, false, true, true]'
oppleoConfig.backupSuccessTimestamp = datetime.today() - timedelta(days=0, hours=3)

print('Last succesful backup: [day ' + str(oppleoConfig.backupSuccessTimestamp.weekday()) + ' = ' + datetime_weekday[oppleoConfig.backupSuccessTimestamp.weekday()] + '] ' + str(oppleoConfig.backupSuccessTimestamp))
print('Now: [day ' + str(datetime.today().weekday()) + ' = ' + datetime_weekday[datetime.today().weekday()] + '] ' + str(datetime.today()))
print(oppleoConfig.backupInterval + " CalDay:" + oppleoConfig.BACKUP_INTERVAL_CALDAY + " WeekDay:" + oppleoConfig.BACKUP_INTERVAL_WEEKDAY)

# Sunday = 0, Saturday = 6
weekday = ['Zondag', 'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag']
backupIntervalWeekday = json.loads(oppleoConfig.backupIntervalWeekday)
s = ''
for idx, val in enumerate(backupIntervalWeekday):
  if len(s) > 0:
    s += ', '
  s += (weekday[idx] + ': ' + str(val))
print(s)

print('Backup time: ' + str(oppleoConfig.backupTimeOfDay))

due = b.isBackupDue()
print('Backup due: ' + str(due))

print ('Done')
"""
b.setBackupCalDay()
# b.__purgeLocalBackups__()


ct1, ct1l = b.listSMBFilesAndDirectories()
ct2, ct2l = b.listSMBFilesAndDirectories(hideFiles=True)

for dirn in ct2l:
    ct3, ct3l = b.listSMBFilesAndDirectories(hideFiles=True, smbPath=ct2 + dirn)
    ct4, ct4l = b.listSMBFilesAndDirectories(hideDirectories=True, smbPath=ct2 + dirn)

lbudir, lbulist = b.__listLocalBackups__()
rbudir, rbulist = b.__listSMBBackups__()

shares = b.__listSMBShares__()

#filename = b.createBackup()
filename = 'backup_2021-02-02_18.07.58_laadpaal_noord.zip'
filepath = '/Users/laeme498/Projects/Oppleo/backup/'
b.__storeBackupToSmbShare__(filename, filepath)
"""

""" 
- backup
    - enable backup [checkbox]
      - number of local backups to keep
      - when
        - daily, hourly, weekly, monthly
        - after end of charge
      [ folder niet wijzigbaar ]

    - enable remote backup [SMB]
      - ip adres/ servername
      - username
      - password
      - connect
        - select share
        - select folder/ create folder
        - done

    - list backups
      - local
      - remote [SMB]

        - view backup
        - validate backup

"""
