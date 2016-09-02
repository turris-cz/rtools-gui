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

CREATE TABLE last_seen_ram (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20) NOT NULL,
    phase char(1) NOT NULL, -- tests/steps
    size int NOT NULL, -- in GB
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE last_seen_ram OWNER TO omnia_flasher;

CREATE TABLE last_seen_eeprom (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20) NOT NULL,
    phase char(1) NOT NULL, -- tests/steps
    eeprom text NOT NULL,
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE last_seen_eeprom OWNER TO omnia_flasher;

CREATE TABLE last_seen_mcu (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20) NOT NULL,
    bootloader_md5 char(32) NOT NULL,
    image_md5 char(32) NOT NULL,
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE last_seen_mcu OWNER TO omnia_flasher;

CREATE TABLE last_seen_uboot (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20) NOT NULL,
    image_md5 char(32) NOT NULL,
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE last_seen_uboot OWNER TO omnia_flasher;

CREATE OR REPLACE VIEW good_routers AS
    SELECT routers.id, MIN(runs.start) AS first_success, MAX(runs.start) AS last_success FROM routers
    INNER JOIN runs ON routers.id = runs.router
    WHERE runs.success = true
    GROUP BY routers.id
    ORDER BY routers.id;
ALTER VIEW good_routers OWNER TO omnia_flasher;

CREATE TABLE results (
    id varchar(20) NOT NULL,
    time timestamp NOT NULL DEFAULT current_timestamp,
    phase char(1) NOT NULL, -- tests/steps
    result boolean NOT NULL, -- true passed, false failed
    FOREIGN KEY (id) REFERENCES routers (id) ON DELETE CASCADE
);
ALTER TABLE results OWNER TO omnia_flasher;

CREATE OR REPLACE FUNCTION router_steps(router_id text)
    RETURNS TABLE ("run_id" bigint, "run_start" timestamp, "attempt" int, "order" int, "time" timestamp, "name" text, "passed" boolean) AS
    $$ SELECT runs.id, runs.start, steps.attempt, steps.step_order, steps.timestamp, steps.step_name, steps.passed FROM runs INNER JOIN steps ON runs.id = steps.run
        WHERE runs.router = router_steps.router_id ORDER BY steps.id
    $$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION router_tests(router_id text)
    RETURNS TABLE ("run_id" bigint, "run_start" timestamp, "attempt" int, "time" timestamp, "name" text, "passed" boolean) AS
    $$ SELECT runs.id, runs.start, tests.attempt, tests.timestamp, tests.test_name, tests.result FROM runs INNER JOIN tests ON runs.id = tests.run
        WHERE runs.router = router_tests.router_id ORDER BY tests.id
    $$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION export_results()
    RETURNS trigger AS
    $$
    BEGIN
        COPY (SELECT to_char(time, 'YYYY-MM-DD HH24:MI:SS'),id,phase,result FROM results ORDER BY time) TO '/tmp/results.csv' WITH CSV DELIMITER ',';
        RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql' SECURITY DEFINER;

CREATE TRIGGER export_csv AFTER INSERT ON results EXECUTE PROCEDURE export_results();
