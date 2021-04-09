-- Config option to display vehicle data on the dashboard
ALTER TABLE charger_config ADD vehicle_data_on_dashboard BOOLEAN;
-- Default disabled
UPDATE charger_config SET vehicle_data_on_dashboard = 'f';
