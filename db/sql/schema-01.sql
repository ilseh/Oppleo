create table session (
    id serial primary key,
    rfid varchar(100) not null,
    start_value float,
    end_value float,
    created_at timestamp,
    modified_at timestamp
);

create table session_measures (
    id serial,
    session_id integer references session(id),
    value float,
    created_at timestamp
);
