ALTER TABLE charger_config ADD smb_backup_server_name varchar(200);
UPDATE charger_config SET smb_backup_server_name = '';

