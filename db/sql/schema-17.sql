-- Daltarief 
-- Meestal op weekdagen van 23.00 tot 7.00 uur en in weekenden en op feestdagen* de gehele dag. 
-- Op officiële feestdagen: Nieuwjaarsdag, Eerste Paasdag, Tweede Paasdag, Koningsdag, Hemelvaartsdag, Eerste Pinksterdag, Tweede Pinksterdag, Eerste Kerstdag en Tweede Kerstdag.

-- feestdag - datum
-- zon/zaterdag - weekdag
-- weekdag 23-07

-- Bijv. Monday   00:00-07:00 en 23:00-23:59

CREATE TABLE off_peak_hours (
   id int PRIMARY KEY,
   weekday VARCHAR (20),
   holiday DATE,
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
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('01/01/2020', '00:00', '23:59', 'Nieuwjaarsdag');
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('01/01/2021', '00:00', '23:59', 'Nieuwjaarsdag');
-- Tweede Paasdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('13/04/2020', '00:00', '23:59', 'Tweede Paasdag');
-- Koningsdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('27/04/2020', '00:00', '23:59', 'Koningsdag');
-- Hemelvaartsdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('21/05/2020', '00:00', '23:59', 'Hemelvaartsdag');
-- Tweede Pinksterdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('01/06/2020', '00:00', '23:59', 'Tweede Pinksterdag');
-- Eerste Kerstdag
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('25/12/2020', '00:00', '23:59', 'Eerste Kerstdag');
-- Tweede Kerstdag.
INSERT INTO off_peak_hours (holiday, off_peak_start, off_peak_end, description) 
   VALUES ('26/12/2020', '00:00', '23:59', 'Tweede Kerstdag');
