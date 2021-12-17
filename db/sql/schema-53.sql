-- Pushover config https://pushover.net/api
ALTER TABLE charger_config ADD pushover_enabled boolean;
ALTER TABLE charger_config ADD pushover_api_key VARCHAR(256);
ALTER TABLE charger_config ADD pushover_user_key VARCHAR(256);
ALTER TABLE charger_config ADD pushover_device VARCHAR(256);
ALTER TABLE charger_config ADD pushover_sound VARCHAR(256);
-- Pushover default 
UPDATE charger_config SET pushover_enabled = 'f';
UPDATE charger_config SET pushover_api_key = '';
UPDATE charger_config SET pushover_user_key = '';
UPDATE charger_config SET pushover_device = '';
UPDATE charger_config SET pushover_sound = '';

-- MQTT config
ALTER TABLE charger_config ADD mqtt_outbound_enabled boolean;
ALTER TABLE charger_config ADD mqtt_host VARCHAR(128);
ALTER TABLE charger_config ADD mqtt_port INT;
ALTER TABLE charger_config ADD mqtt_username VARCHAR(64);
ALTER TABLE charger_config ADD mqtt_password VARCHAR(64);
-- MQTT default 
UPDATE charger_config SET mqtt_outbound_enabled = 'f';
UPDATE charger_config SET mqtt_host = '';
UPDATE charger_config SET mqtt_port = 1880;
UPDATE charger_config SET mqtt_username = '';
UPDATE charger_config SET mqtt_password = '';
