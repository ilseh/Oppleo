-- Add 2FA to users table
-- sqlalchemy does not handle capitals well, at all. Changing 2FA to 2fa in the column name...
ALTER TABLE users DROP enabled_2FA;
ALTER TABLE users ADD enabled_2fa BOOLEAN;
UPDATE users SET enabled_2fa = 'f';
