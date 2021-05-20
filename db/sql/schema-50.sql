--
-- Reminder to self:
--     DO NOT USE CAPITALS IN COLUMN NAMES !!!
--
-- Drop the column with capitals
ALTER TABLE users DROP bypass_local_2FA;
-- Re-create it using lower case...
ALTER TABLE users ADD bypass_local_2fa BOOLEAN;
UPDATE users SET bypass_local_2fa = 'f';-- Add bypass 2FA for local network to users table
