ALTER TABLE charger_config ADD backup_enabled BOOLEAN;
UPDATE charger_config SET backup_enabled = 'f';

ALTER TABLE charger_config ADD backup_interval varchar(1);
UPDATE charger_config SET backup_interval = 'd';

ALTER TABLE charger_config ADD backup_time_of_day TIME;
UPDATE charger_config SET backup_time_of_day = '08:00:00';

ALTER TABLE charger_config ADD backup_local_history INT;
UPDATE charger_config SET backup_local_history = 5;


ALTER TABLE charger_config ADD os_backup_enabled BOOLEAN;
UPDATE charger_config SET os_backup_enabled = 'f';

ALTER TABLE charger_config ADD os_backup_type varchar(20);
UPDATE charger_config SET os_backup_type = '';

ALTER TABLE charger_config ADD smb_backup_ip_address varchar(20);
UPDATE charger_config SET smb_backup_ip_address = '';

ALTER TABLE charger_config ADD smb_backup_username varchar(60);
UPDATE charger_config SET smb_backup_username = '';

ALTER TABLE charger_config ADD smb_backup_password varchar(100);
UPDATE charger_config SET smb_backup_password = '';

ALTER TABLE charger_config ADD smb_backup_share_name varchar(200);
UPDATE charger_config SET smb_backup_share_name = '';

ALTER TABLE charger_config ADD smb_backup_share_path varchar(256);
UPDATE charger_config SET smb_backup_share_path = '/';
