-- Cleanup rfid

-- vehicle_make     Brand of the vehicle, selecting the api
-- api_account      Identity on the api
-- vehicle_vin      Selecting the vehicle
-- vehicle_model    Additional info for reporting
-- license_plate    Additional info for reporting
-- vehicle_name     Additional info for reporting


-- To be deleted (all in teslapy for Tesla): 
-- api_token_type
-- api_access_token
-- api_refresh_token
-- api_created_at
-- api_expires_in
-- vehicle_id

ALTER TABLE rfid DROP api_token_type;
ALTER TABLE rfid DROP api_access_token;
ALTER TABLE rfid DROP api_refresh_token;
ALTER TABLE rfid DROP api_created_at;
ALTER TABLE rfid DROP api_expires_in;
ALTER TABLE rfid DROP vehicle_id;
