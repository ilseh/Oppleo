alter table charger_config ADD enablequickcharge boolean;
UPDATE charger_config SET enablequickcharge = 'f' WHERE charger_name = 'laadpaal_noord';

alter table charger_config ADD reauthwebchargestart boolean;
UPDATE charger_config SET reauthwebchargestart = 't' WHERE charger_name = 'laadpaal_noord';
