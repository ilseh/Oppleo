-- Increase Tesla token size from 100. As of end 2021 it is 1200 chars long.

ALTER TABLE rfid DROP api_access_token;
ALTER TABLE rfid ADD api_access_token VARCHAR(50000);
ALTER TABLE rfid DROP api_refresh_token;
ALTER TABLE rfid ADD api_refresh_token VARCHAR(50000);
