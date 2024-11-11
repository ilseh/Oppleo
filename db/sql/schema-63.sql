-- Add WebAuthN expected origin
ALTER TABLE charger_config ADD behind_ssl_proxy BOOLEAN DEFAULT false;
-- Set  existing to false
UPDATE charger_config SET behind_ssl_proxy = false;

-- Add WebAuthN expected origin
ALTER TABLE webauthn_credentials ADD origin VARCHAR(256);
-- Set  existing to empty
UPDATE webauthn_credentials SET origin = '';
