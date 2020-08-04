alter table charger_config ADD receipt_prefix varchar(20);
UPDATE charger_config SET receipt_prefix = '00000';
