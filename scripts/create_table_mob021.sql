CREATE TABLE mobilite.mob021_shared_mobility
(
    idobj character varying(500) NOT NULL,
    name character varying(500),
    provider_id character varying(500),
    is_installed boolean,
    is_renting boolean,
    is_returning boolean,
    num_bikes_available integer,
    update_time timestamp without time zone,
    last_reported timestamp without time zone,
    store_uri_android character varying(500),
    store_uri_ios character varying(500),
    CONSTRAINT mob021_shared_mobility_pkey PRIMARY KEY (idobj)
)
WITH (
    OIDS = FALSE
);

SELECT AddGeometryColumn ('mobilite', 'mob021_shared_mobility', 'geom', 2056, 'POINT', 2);
 
