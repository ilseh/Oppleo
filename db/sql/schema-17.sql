-- Daltarief 
-- Meestal op weekdagen van 23.00 tot 7.00 uur en in weekenden en op feestdagen* de gehele dag. 
-- Op officiële feestdagen: Nieuwjaarsdag, Eerste Paasdag, Tweede Paasdag, Koningsdag, Hemelvaartsdag, Eerste Pinksterdag, Tweede Pinksterdag, Eerste Kerstdag en Tweede Kerstdag.

-- feestdag - datum
-- zon/zaterdag - weekdag
-- weekdag 23-07

-- Bijv. Monday   00:00-07:00 en 23:00-23:59
-- Recurring = same date each year. Pinksteren and Eastern change each year, Christmas and Kingsday are recurring on the same date

CREATE TABLE off_peak_hours (
   id int PRIMARY KEY,
   weekday VARCHAR (20),
   holiday_day int,
   holiday_month int,
   holiday_year int,
   recurring boolean,
   description VARCHAR(100),
   off_peak_start TIME NOT NULL
   off_peak_end TIME NOT NULL
);

-- Weekday
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Monday', '00:00', '07:00', 'Maandag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Monday', '23:00', '23:59', 'Maandag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Tuesday', '00:00', '07:00', 'Dinsdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Tuesday', '23:00', '23:59', 'Dinsdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Wednesday', '00:00', '07:00', 'Woensdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Wednesday', '23:00', '23:59', 'Woensdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Thursday', '00:00', '07:00', 'Donderdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Thursday', '23:00', '23:59', 'Donderdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Friday', '00:00', '07:00', 'Vrijdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Friday', '23:00', '23:59', 'Vrijdag');

-- Weekend
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Saturday', '00:00', '23:59', 'Zaterdag');
INSERT INTO off_peak_hours (weekday, off_peak_start, off_peak_end, description) 
   VALUES ('Sunday', '00:00', '23:59', 'Zondag');

-- Nieuwjaarsdag
INSERT INTO off_peak_hours (holiday_day, holiday_month, holiday_year, off_peak_start, off_peak_end, description, recurring) 
   VALUES (1, 1, 2020, '00:00', '23:59', 'Nieuwjaarsdag', 't');
-- Tweede Paasdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (13, 4, 2020, '00:00', '23:59', 'Tweede Paasdag', 'f');
-- Koningsdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (27, 4, 2020, '00:00', '23:59', 'Koningsdag', 't');
-- Hemelvaartsdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (21, 5, 2020, '00:00', '23:59', 'Hemelvaartsdag', 'f');
-- Tweede Pinksterdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (1, 6, 2020, '00:00', '23:59', 'Tweede Pinksterdag', 'f');
-- Eerste Kerstdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (25, 12, 2020, '00:00', '23:59', 'Eerste Kerstdag', 't');
-- Tweede Kerstdag.
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description, recurring) 
   VALUES (26, 12, 2020, '00:00', '23:59', 'Tweede Kerstdag', 't');
