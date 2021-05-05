-- Add 2FA to users table
-- Add shared secret to table (hex(16))
ALTER TABLE users ADD shared_secret varchar(64);
-- Default disabled
UPDATE users SET shared_secret = '';
-- Add shared secret to table
ALTER TABLE users ADD enabled_2FA BOOLEAN;
-- Default disabled
UPDATE users SET enabled_2FA = 'f';
