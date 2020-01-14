alter table "session" RENAME COLUMN "created_at" TO "start_time";
alter table "session" RENAME COLUMN "modified_at" TO "end_time";
alter table "session" ADD "tariff" float;
alter table "session" ADD "total_energy" float;
alter table "session" ADD "total_price" float;