alter table energy_device ADD column baudrate int;
alter table energy_device ADD column bytesize int;
alter table energy_device ADD column parity char(1);
alter table energy_device ADD column stopbits int;
alter table energy_device ADD column timeout int;
alter table energy_device ADD column debug boolean;
alter table energy_device ADD column mode varchar(10);

update energy_device 
        set baudrate = 9600, 
            bytesize = 8, 
            parity = 'N', 
            stopbits=1, 
            timeout=1, 
            debug='t', 
            mode='rtu'
        where energy_device_id = 'laadpaal_noord';


