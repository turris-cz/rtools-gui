-- For now
DROP DATABASE mox_boards;
-- TODO drop

CREATE ROLE mox_rtools;
ALTER ROLE mox_rtools LOGIN PASSWORD 'VI7QNfDvJtmnrpQ5';
CREATE DATABASE mox_boards WITH OWNER mox_rtools;

\c mox_boards

CREATE TABLE boards (
	serial bigint NOT NULL PRIMARY KEY,
	mac_wan macaddr,
	mac_sgmii macaddr,
	revision smallint NOT NULL,
	type varchar(1) NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
ALTER TABLE boards OWNER TO mox_rtools;
COMMENT ON COLUMN boards.serial IS 'Serial number of board (8 unsigned bytes)';
COMMENT ON COLUMN boards.mac_wan IS 'Mac address for WAN interface on MOX A';
COMMENT ON COLUMN boards.mac_sgmii IS 'Mac address for SGMII interface on MOX A';
COMMENT On COLUMN boards.revision IS 'Board revision number';
COMMENT ON COLUMN boards.type IS 'Board type. It is single character business identifier.';

-- TODO DROP
-- Use these only in insecure mode!!!!
INSERT INTO boards (serial, revision, type) VALUES
	(56639881216, 21, 'A'), -- 30
	(56656658432, 20, 'D'), -- 31
	(56673435648, 0, 'B'), -- 32
	(56690212864, 21, 'C'), -- 33
	(56706990080, 0, 'E'), -- 34
	(56723767296, 0, 'F'), -- 35
	(56740544512, 0, 'G') -- 36
	;
-- TODO DROP

CREATE TABLE core_info (
	id bigserial PRIMARY KEY,
	board bigint REFERENCES boards (serial),
	mem_size smallint NOT NULL,
	key text NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
ALTER TABLE core_info OWNER TO mox_rtools;
COMMENT ON COLUMN core_info.mem_size IS 'Size of RAM in MiB';
COMMENT ON COLUMN core_info.key IS 'Public key for private key of Turris MOX';

CREATE TABLE programmer_state (
	id serial PRIMARY KEY,
	hostname varchar(50) NOT NULL,
	rtools_hash varchar(40) NOT NULL,
	secure_firmware varchar(64) NOT NULL,
	uboot varchar(64) NOT NULL,
	rescue varchar(64) NOT NULL,
	dtb varchar(64) NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
ALTER TABLE programmer_state OWNER TO mox_rtools;
COMMENT ON COLUMN programmer_state.hostname IS 'Hostname of programmer';
COMMENT ON COLUMN programmer_state.rtools_hash IS 'git hash of used rtools-gui repository';
COMMENT ON COLUMN programmer_state.secure_firmware IS 'sha256sum of used secure-firmware';
COMMENT ON COLUMN programmer_state.uboot IS 'sha256sum of used u-boot';
COMMENT ON COLUMN programmer_state.rescue IS 'sha256sum of used rescue image';
COMMENT ON COLUMN programmer_state.dtb IS 'sha256sum of used DTB';

CREATE TABLE runs (
	id bigserial PRIMARY KEY,
	board bigint REFERENCES boards (serial),
	programmer bigint REFERENCES programmer_state(id),
	programmer_id smallint,
	steps text[] NOT NULL,
	success boolean NOT NULL DEFAULT false,
	tstart timestamp NOT NULL DEFAULT current_timestamp,
	tend timestamp
);
ALTER TABLE runs OWNER TO mox_rtools;
COMMENT ON COLUMN runs.programmer_id IS 'ID of used programmer board';
COMMENT ON COLUMN runs.steps IS 'Planned steps (not executed ones those are in steps table)';
COMMENT ON COLUMN runs.success IS 'If run reached last step without error or warning';
COMMENT ON COLUMN runs.tstart IS 'Time of run execution start.';
COMMENT ON COLUMN runs.tend IS 'Time of run execution end.';

CREATE TABLE steps (
	id bigserial PRIMARY KEY,
	step_name text NOT NULL,
	run bigint REFERENCES runs (id),
	success boolean NOT NULL DEFAULT false,
	message text,
	tstart timestamp NOT NULL DEFAULT current_timestamp,
	tend timestamp
);
ALTER TABLE steps OWNER TO mox_rtools;
COMMENT ON COLUMN steps.step_name IS 'Name of step it self. Used to identify this step.';
COMMENT ON COLUMN steps.success IS 'Boolean if step passed successfully.';
COMMENT ON COLUMN steps.message IS 'Error or warning message produced by this step';
COMMENT ON COLUMN steps.tstart IS 'Time of step execution start.';
COMMENT ON COLUMN steps.tend IS 'Time of step execution end. Should be consistend with message addition.';
