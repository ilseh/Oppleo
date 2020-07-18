alter table charger_config DROP enablequickcharge;
alter table charger_config DROP reauthwebchargestart;

alter table charger_config ADD webcharge_on_dashboard boolean;
UPDATE charger_config SET webcharge_on_dashboard = 'f' WHERE charger_name = 'laadpaal_noord';

alter table charger_config ADD auth_webcharge boolean;
UPDATE charger_config SET auth_webcharge = 't' WHERE charger_name = 'laadpaal_noord';
