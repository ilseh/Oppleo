alter table "energy_device" ADD "baudrate" int;
alter table "energy_device" ADD "bytesize" int;

alter table "energy_device" ADD "parity" char(1);
alter table "energy_device" ADD "stopbits" int;
alter table "energy_device" ADD "timeout_value" int;
alter table "energy_device" ADD "debug" boolean;
alter table "energy_device" ADD "mode" varchar(10);

update energy_device 
        set baudrate = 9600, 
            bytesize = 8, 
            parity = 'N', 
            stopbits=1, 
            timeout_value=1, 
            debug='t', 
            mode='rtu',
        where energy_device_id = 'laadpaal_noord';


