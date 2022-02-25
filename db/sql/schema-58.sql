-- Change modbus timeout from seconds to optionally sub second
-- 0.05 is the default timeout

UPDATE energy_device SET serial_timeout = 0.05;
