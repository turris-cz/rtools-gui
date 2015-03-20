CREATE ROLE tflasher LOGIN PASSWORD 'poiuytrewq';

CREATE DATABASE turris WITH OWNER tflasher;

\c turris

CREATE TABLE routers (
    id varchar(20),
    attempt int CHECK (attempt >= 0) DEFAULT '0',
    add_time timestamp NOT NULL DEFAULT current_timestamp,
    status int NOT NULL CHECK (status >= 0) DEFAULT '0',
    error text NOT NULL DEFAULT '',
    PRIMARY KEY (id, attempt)
);
ALTER TABLE routers OWNER TO tflasher;

CREATE TABLE tests (
    id varchar(20),
    attempt int,
    serie int NOT NULL CHECK (serie >= 0),
    testid int NOT NULL,
    testresult int NOT NULL,
    msg text DEFAULT NULL,
    PRIMARY KEY (id, attempt, serie, testid),
    FOREIGN KEY (id, attempt) REFERENCES routers (id, attempt) ON DELETE CASCADE
);
ALTER TABLE tests OWNER TO tflasher;

CREATE VIEW good_routers AS
    SELECT DISTINCT id, attempt, add_time FROM routers
    LEFT JOIN tests USING (id, attempt)
    GROUP BY id, attempt, serie
    HAVING max(testresult)='0' AND count(*)='9'
    ORDER BY id;
ALTER VIEW good_routers OWNER TO tflasher;

CREATE TABLE last_seen_firmware (
    time timestamp NOT NULL DEFAULT current_timestamp,
    id varchar(20),
    attempt int,
    firmware text NOT NULL DEFAULT '',
    FOREIGN KEY (id, attempt) REFERENCES routers (id, attempt) ON DELETE CASCADE
);
ALTER TABLE last_seen_firmware OWNER TO tflasher;
