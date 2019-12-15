create table session (
    id serial,
    rfid varchar(100) not null,
    start_value float,
    end_value float,
    created_at date,
    modified_at date
);
