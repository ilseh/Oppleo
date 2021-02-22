-- 0 = Sunday, 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday
UPDATE charger_config SET backup_interval_weekday = '[false, false, false, false, false, false, false]';

-- 0 is the first of the month
ALTER TABLE charger_config DROP backup_interval_calday;
ALTER TABLE charger_config ADD backup_interval_calday varchar(300);
UPDATE charger_config SET backup_interval_calday = '[false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]';