#!/bin/sh
#
start=`date +%s`

DB_USER=charger
DB_PASS=charger
DB_NAME=charger
DB_HOSTNAME=localhost
DB_PORT=5432

# DIR holds the directory of the backup script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo " Backup dir ${DIR}..."

DATESTAMP=$(date +%Y-%m-%d"_"%H.%Mh)
 
# remove backups older than $DAYS_KEEP
#DAYS_KEEP=30
#find ${DIR}* -mtime +$DAYS_KEEP -exec rm -f {} \; 2&gt; /dev/null
 
# remove all backups except the $KEEP latest
KEEP=5
BACKUPS=`find ${DIR} -name "pg_dump-*.dump" | wc -l | sed 's/\ //g'`
while [ $BACKUPS -ge $KEEP ]
do
  ls -tr1 ${DIR}/pg_dump-*.dump | head -n 1 | xargs rm -f
  BACKUPS=`expr $BACKUPS - 1`
done
 
#
# create backups securely
#umask 006
 
# dump all the databases in a gzip file
FILENAME=${DIR}/pg_dump-${DATESTAMP}.dump
/usr/bin/pg_dump --dbname=postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME -Fc > $FILENAME

end=`date +%s`
runtime=$((end-start))

ls -l1h ${DIR}/pg_dump-*.dump | awk '{print $9, $6, $7, $8, $5}'
echo "Backup in $runtime seconds"
