-- Add bypass 2FA for local network to users table
ALTER TABLE users ADD bypass_local_2FA BOOLEAN;
UPDATE users SET bypass_local_2FA = 'f';