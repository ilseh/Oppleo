-- Step 1 in changing the energy_device column name from smb_backup_ip_address to 
--        smb_backup_servername_or_ip_address by adding the new collumn now and deleting
--        the smb_backup_ip_address column in a following release 
--        In step 2 the following queries will delete the columns.
--          alter table charger_config DROP smb_backup_ip_address;
--          alter table charger_config DROP smb_backup_server_name;
ALTER TABLE charger_config ADD smb_backup_servername_or_ip_address varchar(20);
