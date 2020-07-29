alter table charger_config ADD allow_local_dashboard_access boolean;
UPDATE charger_config SET allow_local_dashboard_access = 'f';

alter table charger_config ADD router_ip_address varchar(20);;
UPDATE charger_config SET router_ip_address = '10.0.0.1';
