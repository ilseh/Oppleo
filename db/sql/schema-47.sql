-- Extend router_ip_address to allow a list rather than a single IP address value
-- Change router_ip_address column from 20 to 1024 chars
ALTER TABLE charger_config ALTER COLUMN router_ip_address type character varying(1024);