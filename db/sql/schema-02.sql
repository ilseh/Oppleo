
-- rename of device_1 to laadpaal_noord
insert into energy_device values ('laadpaal_noord', '/dev/ttyUSB0', 1);
update energy_device_measures set energy_device_id = 'laadpaal_noord' where energy_device_id = 'device_1';
delete from energy_device where energy_device_id = 'device_1';
