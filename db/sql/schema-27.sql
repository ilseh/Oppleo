alter table charger_config ADD restrict_dashboard_access boolean;
UPDATE charger_config SET restrict_dashboard_access = 'f';

alter table charger_config ADD restrict_menu boolean;
UPDATE charger_config SET restrict_menu = 'f';
