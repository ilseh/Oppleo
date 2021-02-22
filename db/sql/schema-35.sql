-- Step 2 in changing the energy_device column name from smb_backup_share_name to smb_backup_service_name  
--        and smb_backup_share_path to smb_backup_remote_path
ALTER TABLE charger_config DROP smb_backup_share_path;
ALTER TABLE charger_config DROP smb_backup_share_name;
--ALTER TABLE charger_config DROP smb_backup_server_name;

-- Add backup interval details
ALTER TABLE charger_config ADD backup_interval_weekday varchar(200);
ALTER TABLE charger_config ADD backup_interval_calday varchar(200);

-- Step 2 in changing the energy_device column name from smb_backup_ip_address to 
--        smb_backup_servername_or_ip_address
ALTER TABLE charger_config DROP smb_backup_ip_address;
ALTER TABLE charger_config DROP smb_backup_server_name;

-- Offsite backup hsitory
ALTER TABLE charger_config ADD os_backup_history INT;
UPDATE charger_config SET os_backup_history = 5;