
alter table charger_config DROP secret_key ;
alter table charger_config DROP wtf_csrf_secret_key ;

alter table charger_config DROP httphost ;
alter table charger_config DROP httpPort ;
alter table charger_config DROP usereloader ;

alter table charger_config DROP factorwhkm ;

alter table charger_config DROP autosessionenabled ;
alter table charger_config DROP autosessionminutes ;
alter table charger_config DROP autosessionenergy ;
alter table charger_config DROP autosessioncondenseSameOdometer ;

alter table charger_config DROP pulseledmin ;
alter table charger_config DROP pulseledmax ;
alter table charger_config DROP gpiomode ;
alter table charger_config DROP pinledred ;
alter table charger_config DROP pinledgreen ;
alter table charger_config DROP pinledblue ;
alter table charger_config DROP pinbuzzer;

alter table charger_config DROP peakhoursoffpeakenabled;
alter table charger_config DROP peakhoursallowpeakoneperiod;

alter table charger_config DROP prowlenabled;
alter table charger_config DROP prowlapiKey;



alter table charger_config ADD secret_key varchar(100);
alter table charger_config ADD wtf_csrf_secret_key varchar(100);

alter table charger_config ADD http_host varchar(64);
alter table charger_config ADD http_port int;
alter table charger_config ADD use_reloader boolean;

alter table charger_config ADD factor_whkm int;

alter table charger_config ADD autosession_enabled boolean;
alter table charger_config ADD autosession_minutes int;
alter table charger_config ADD autosession_energy float;
alter table charger_config ADD autosession_condense_same_odometer boolean;

alter table charger_config ADD pulseled_min int;
alter table charger_config ADD pulseled_max int;
alter table charger_config ADD gpio_mode varchar(10);
alter table charger_config ADD pin_led_red int;
alter table charger_config ADD pin_led_green int;
alter table charger_config ADD pin_led_blue int;
alter table charger_config ADD pin_buzzer int;

alter table charger_config ADD peakhours_offpeak_enabled boolean;
alter table charger_config ADD peakhours_allow_peak_one_period boolean;

alter table charger_config ADD prowl_enabled boolean;
alter table charger_config ADD prowl_apiKey varchar(100);


UPDATE charger_config SET secret_key = 'abcdefghijklmnopqrstuvwxyz1234567890' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET wtf_csrf_secret_key = 'abcdefghijklmnopqrstuvwxyz1234567890' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET http_host = '0.0.0.0' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET http_port = 80 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET use_reloader = 'f' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET factor_whkm = 162 WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET autosession_enabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosession_minutes = 90 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosession_energy = 0.1 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosession_condense_same_odometer = 't' WHERE charger_name = 'laadpaal_noord';


UPDATE charger_config SET pulseled_min = 3 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pulseled_max = 98 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET gpio_mode = 'BCM' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pin_led_red = 13 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pin_led_green = 12 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pin_led_blue = 16 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pin_buzzer = 23 WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET peakhours_offpeak_enabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET peakhours_allow_peak_one_period = 'f' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET prowl_enabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET prowl_apiKey = '5df94c19d71b4b456efcb49996406fa62e717a44' WHERE charger_name = 'laadpaal_noord';
