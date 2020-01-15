alter table "rfid" RENAME COLUMN "allow" TO "enabled";
alter table "rfid" RENAME COLUMN "vehicle" TO "vehicle_make";
alter table "rfid" alter column "vehicle_make" type varchar(100);
alter table "rfid" ADD "vehicle_model" varchar(100);
alter table "rfid" ADD "get_odometer" boolean;

alter table "rfid" ADD "api_access_token" varchar(100);
alter table "rfid" ADD "api_token_type" varchar(100);
alter table "rfid" ADD "api_created_at" varchar(100);
alter table "rfid" ADD "api_expires_in" varchar(100);
alter table "rfid" ADD "api_refresh_token" varchar(100);
