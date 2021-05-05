-- Add 2FA to users table
-- Change shared secret column from 64 to 256 chars
ALTER TABLE users ALTER COLUMN shared_secret type character varying(256);
