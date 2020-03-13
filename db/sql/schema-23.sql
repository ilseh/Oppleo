alter table charger_config ADD log_file varchar(256);

UPDATE charger_config SET log_file = '/tmp/Oppleo.log' WHERE charger_name = 'laadpaal_noord';
