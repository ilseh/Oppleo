alter table energy_device ADD modbus_config varchar(100);

UPDATE energy_device SET modbus_config = 'SDM630v2';
