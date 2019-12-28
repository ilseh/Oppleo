create table session (
    id serial primary key,
    rfid varchar(100) not null,
    start_value float,
    end_value float,
    created_at timestamp,
    modified_at timestamp
);

create table energy_device (
    energy_device_id varchar(100) primary key
);

insert into energy_device values ('device_1');

create table energy_device_measures (
    id serial primary key,
    energy_device_id varchar(100) references energy_device(energy_device_id),
    kwh_l1 float,
    kwh_l2 float,
    kwh_l3 float,
    a_l1 float,
    a_l2 float,
    a_l3 float,
    kw_total float,
    created_at timestamp
);
