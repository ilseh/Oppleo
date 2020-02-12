alter table energy_device ADD column close_port_after_each_call boolean;
alter table energy_device ADD column modbus_timeout int;

alter table energy_device RENAME column timeout TO serial_timeout;

update energy_device set baudrate = 38400 where energy_device_id = 'laadpaal_noord';
update energy_device set close_port_after_each_call = 't' where energy_device_id = 'laadpaal_noord';
update energy_device set modbus_timeout = 2 where energy_device_id = 'laadpaal_noord';

