-- Add avatar to user

ALTER TABLE users ADD avatar varchar(256);
-- Default 
UPDATE users SET avatar = 'unknown.png';
