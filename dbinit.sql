CREATE ROLE tflasher LOGIN PASSWORD 'poiuytrewq';

CREATE DATABASE turris OWNER tflasher;

CREATE TABLE routers (
    id varchar(20) PRIMARY KEY,
    status int NOT NULL CHECK (status >= 0),
    error text NOT NULL
);

