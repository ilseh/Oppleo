-- Bypass to enforce
ALTER TABLE users DROP bypass_local_2fa;
-- Re-create it using lower case...
ALTER TABLE users ADD enforce_local_2fa BOOLEAN;
UPDATE users SET enforce_local_2fa = 't';-- Add bypass 2FA for local network to users table
