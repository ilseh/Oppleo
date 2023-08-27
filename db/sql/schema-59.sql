-- Change charger name to an ID, and add a charger name string to allow special characters including spaces

-- Rename the name to ID
ALTER TABLE charger_config RENAME COLUMN charger_name TO charger_id;
-- Add the free-text name field
ALTER TABLE charger_config ADD charger_name_text VARCHAR(100);

-- Copy all existing IDs to the new name field
UPDATE charger_config SET charger_name_text = charger_id
