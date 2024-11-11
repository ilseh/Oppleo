-- Add WebAuthN expected origin
ALTER TABLE charger_config ADD webauthn_expected_origin VARCHAR(200);
-- Copy all existing IDs to the new name field
UPDATE charger_config SET webauthn_expected_origin = '';