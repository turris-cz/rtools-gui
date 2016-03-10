CREATE ROLE omnia_flasher LOGIN PASSWORD 'poiuytrewq';

CREATE DATABASE omnia_flashing WITH OWNER omnia_flasher;

\c omnia_flashing

CREATE TABLE routers (
    id varchar(20) NOT NULL PRIMARY KEY,
    add_time timestamp NOT NULL DEFAULT current_timestamp
);
ALTER TABLE routers OWNER TO omnia_flasher;

CREATE TABLE runs (
    id bigserial NOT NULL PRIMARY KEY,
    start timestamp NOT NULL DEFAULT current_timestamp,
    router varchar(20) NOT NULL,
    success boolean NOT NULL DEFAULT false,
    FOREIGN KEY (router) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE runs OWNER TO omnia_flasher;

CREATE TABLE steps (
    id bigserial NOT NULL PRIMARY KEY,
    run int NOT NULL,
    timestamp timestamp NOT NULL DEFAULT current_timestamp,
    step_name text NOT NULL,
    step_order int NOT NULL CHECK (step_order >= 0),
    attempt int NOT NULL CHECK (attempt >= 0),
    passed boolean NOT NULL DEFAULT false,
    FOREIGN KEY (run) REFERENCES runs (id) ON DELETE CASCADE
);
ALTER TABLE steps OWNER TO omnia_flasher;

CREATE TABLE tests (
    id bigserial PRIMARY KEY,
    run int NOT NULL,
    timestamp timestamp NOT NULL DEFAULT current_timestamp,
    test_name text NOT NULL,
    result boolean NOT NULL, -- true passed, false failed
    attempt int NOT NULL CHECK (attempt >= 0) DEFAULT '0',
    FOREIGN KEY (run) REFERENCES runs (id) ON DELETE CASCADE
);
ALTER TABLE tests OWNER TO omnia_flasher;

CREATE TABLE last_seen_firmware (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20) NOT NULL,
    firmware text NOT NULL DEFAULT '',
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE last_seen_firmware OWNER TO omnia_flasher;

CREATE OR REPLACE VIEW good_routers AS
    SELECT routers.id, MIN(runs.start) AS first_success, MAX(runs.start) AS last_success FROM routers
    INNER JOIN runs ON routers.id = runs.router
    WHERE runs.success = true
    GROUP BY routers.id
    ORDER BY routers.id;
ALTER VIEW good_routers OWNER TO omnia_flasher;
