# Backing up Oppleo

For a total backup of Oppleo you should backup the database and the `oppleo.ini` file. The database contains the meter-readings history,
registered rfid cards, most settings, and the transactions. The `oppleo.ini` file in the `src/nl/oppleo/config/` 
subdirectory in the Oppleo directory contains the database credentials and elementary settings. 

Backup is a two stage process. First the database tables are dumped to a file, and next the dump file is copied together with
the ini file to another storage location. From there you can imagine off site backups etc.


## 1. Dumping the database to a file

Running the `backup.sh` script creates a file with a backup (dump) of the postgres database in the same location the 
`backup.sh` script is in. The script is in the `db/backup` subdirectory in the Oppleo directory, and the backup dumps will be there as 
well, however you can move the file weherever you want.
The filename is of type `pg_dump-2020-02-23_07.02h.dump` with a readable timestamp. 

The `backup.sh` will keeps the last 5 dumps based on the system (file) timestamp (not the name). 

Run the `backup.sh` script to see if it is working before addin to the crontab.


## 2. Add `backup.sh` to the crontab

Open the crontab using `crontab -e`. On the first time you need to select an editor, Nano is easy with all hotkey hints 
on the bottom. To run the script every day at midnight add `0 0 * * *  /home/pi/oppleo/db/backup/backup.sh`

I have off-peak charging which starts at 23:00h, should be done in the morning, so I backup[ after that at 7am using
`0 7 * * *  /home/pi/oppleo/db/backup/backup.sh`

Save and exit with `ctrl-x` and selecting `Yes`.

You should see a dump file appear every day in the backup.sh directory (probably /home/pi/oppleo/db/backup)


## 3. Backup off-system

To overcome corrupt sd cards it is smart to backup the database to a different system, like a NAS or similar.


