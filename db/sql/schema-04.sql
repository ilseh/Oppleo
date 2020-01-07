alter table session add column energy_device_id varchar(100) references energy_device(energy_device_id);

update session set energy_device_id='laadpaal_noord' where energy_device_id is null;

alter table session alter column energy_device_id set not null;