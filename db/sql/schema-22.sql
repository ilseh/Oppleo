alter table charger_config ADD modbus_interval int;

UPDATE charger_config SET modbus_interval = 10 WHERE charger_name = 'laadpaal_noord';
