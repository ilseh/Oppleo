create table rfid (
    rfid varchar(100) not null,
    allow boolean,
    created_at timestamp,
    last_used_at timestamp
);


insert into rfid (rfid, allow, created_at) values ('856853722117', true, now());

