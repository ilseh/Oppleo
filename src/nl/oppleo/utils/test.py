from nl.oppleo.utils.BackupUtil import BackupUtil

b = BackupUtil()

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

print('Done')