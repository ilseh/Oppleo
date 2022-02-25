-- Change modbus timeout from seconds to optionally sub second

ALTER TABLE energy_device DROP serial_timeout;
ALTER TABLE energy_device ADD serial_timeout float;
UPDATE energy_device SET serial_timeout = 0.5;
