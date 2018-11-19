---- dbinit.sql
--
-- Drop and re-create mox_boards development database

-- For now
DROP DATABASE mox_boards;
-- TODO drop

CREATE ROLE mox_rtools;
ALTER ROLE mox_rtools LOGIN PASSWORD 'VI7QNfDvJtmnrpQ5';
CREATE DATABASE mox_boards WITH OWNER mox_rtools;
