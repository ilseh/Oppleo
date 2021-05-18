-- Wakeup vehicke when requesting for instance charge status
alter table charger_config ADD wakeup_vehicle_on_data_request boolean;
UPDATE charger_config SET wakeup_vehicle_on_data_request = 'f';
