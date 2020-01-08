
alter table rfid add column name varchar(100),
    add column vehicle varchar(100),
    add column license_plate varchar(20),
    add column valid_from timestamp,
    add column valid_until timestamp;

