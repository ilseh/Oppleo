-- Step 1 in changing the energy_device column name from smb_backup_share_name to smb_backup_service_name  
--        and smb_backup_share_path to smb_backup_remote_path
--        In step 2 the following queries will delete the columns.
--          alter table charger_config DROP smb_backup_server_name;
--          alter table charger_config DROP smb_backup_share_name;
ALTER TABLE charger_config ADD smb_backup_service_name varchar(200);
ALTER TABLE charger_config ADD smb_backup_remote_path varchar(256);
