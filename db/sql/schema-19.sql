
alter table charger_config ADD secret_key varchar(100);
alter table charger_config ADD wtf_csrf_secret_key varchar(100);

alter table charger_config ADD httphost varchar(64);
alter table charger_config ADD httpPort int;
alter table charger_config ADD usereloader boolean;

alter table charger_config ADD factorwhkm int;

alter table charger_config ADD autosessionenabled boolean;
alter table charger_config ADD autosessionminutes int;
alter table charger_config ADD autosessionenergy float;
alter table charger_config ADD autosessioncondenseSameOdometer boolean;

alter table charger_config ADD pulseledmin int;
alter table charger_config ADD pulseledmax int;
alter table charger_config ADD gpiomode varchar(10);
alter table charger_config ADD pinledred int;
alter table charger_config ADD pinledgreen int;
alter table charger_config ADD pinledblue int;
alter table charger_config ADD pinbuzzer int;

alter table charger_config ADD peakhoursoffpeakenabled boolean;
alter table charger_config ADD peakhoursallowpeakoneperiod boolean;

alter table charger_config ADD prowlenabled boolean;
alter table charger_config ADD prowlapiKey varchar(100);


UPDATE charger_config SET secret_key = 'abcdefghijklmnopqrstuvwxyz1234567890' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET wtf_csrf_secret_key = 'abcdefghijklmnopqrstuvwxyz1234567890' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET httphost = '0.0.0.0' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET httpPort = 80 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET usereloader = 'f' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET factorwhkm = 162 WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET autosessionenabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosessionminutes = 90 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosessionenergy = 0.1 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET autosessioncondenseSameOdometer = 't' WHERE charger_name = 'laadpaal_noord';


UPDATE charger_config SET pulseledmin = 3 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pulseledmax = 98 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET gpiomode = 'BCM' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pinledred = 13 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pinledgreen = 12 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pinledblue = 16 WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET pinbuzzer = 23 WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET peakhoursoffpeakenabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET peakhoursallowpeakoneperiod = 'f' WHERE charger_name = 'laadpaal_noord';

UPDATE charger_config SET prowlenabled = 't' WHERE charger_name = 'laadpaal_noord';
UPDATE charger_config SET prowlapiKey = '5df94c19d71b4b456efcb49996406fa62e717a44' WHERE charger_name = 'laadpaal_noord';
