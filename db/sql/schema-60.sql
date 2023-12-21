-- Change debug column in energy_device table to simulate. Debug is also a Class method.

-- Rename the debug column to simulate
ALTER TABLE energy_device RENAME COLUMN debug TO simulate;
