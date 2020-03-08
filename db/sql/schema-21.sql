alter table charger_config ADD pin_evse_switch int;
alter table charger_config ADD pin_evse_led int;



UPDATE charger_config SET pin_evse_switch = 5 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pin_evse_led = 6 WHERE charger_name = 'laadpaal_noord';
