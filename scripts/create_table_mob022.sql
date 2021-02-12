CREATE TABLE mobilite.mob022_electric_stations
(
    idobj character varying(500) NOT NULL,
    description character varying,
    availability character varying(200),
    CONSTRAINT mob022_electric_stations_pkey PRIMARY KEY (idobj)
)
WITH (
    OIDS = FALSE
);

SELECT AddGeometryColumn ('mobilite', 'mob022_electric_stations', 'geom', 2056, 'POINT', 2);
 