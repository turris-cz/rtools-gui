CREATE ROLE tflasher LOGIN PASSWORD 'poiuytrewq';

CREATE DATABASE turris OWNER tflasher;

CREATE TABLE routers (
    id varchar(20),
    attempt int CHECK (attempt >= 0) DEFAULT '0',
    add_time timestamp NOT NULL DEFAULT current_timestamp,
    status int NOT NULL CHECK (status >= 0) DEFAULT '0',
    error text NOT NULL DEFAULT '',
    PRIMARY KEY (id, attempt)
);

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
