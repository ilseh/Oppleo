create table session (
    ID SERIAL,
    RFID varchar(100) not null,
    created_at date,
    modified_at date
);
