-- make kWh device optional
ALTER TABLE energy_device ADD device_enabled BOOLEAN;
UPDATE energy_device SET device_enabled = 'f';
