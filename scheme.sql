---- scheme.sql
--
-- Create db scheme for Mox programmer

CREATE TABLE boards (
	serial bigint NOT NULL PRIMARY KEY,
	mac_wan macaddr,
	mac_sgmii macaddr,
	revision smallint NOT NULL,
	type varchar(1) NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN boards.serial IS 'Serial number of board (8 unsigned bytes)';
COMMENT ON COLUMN boards.mac_wan IS 'Mac address for WAN interface on MOX A';
COMMENT ON COLUMN boards.mac_sgmii IS 'Mac address for SGMII interface on MOX A';
COMMENT On COLUMN boards.revision IS 'Board revision number';
COMMENT ON COLUMN boards.type IS 'Board type. It is single character business identifier.';

CREATE TABLE core_info (
	serial bigint PRIMARY KEY REFERENCES boards (serial),
	mem_size smallint NOT NULL,
	key text NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN core_info.mem_size IS 'Size of RAM in MiB';
COMMENT ON COLUMN core_info.key IS 'Public key for private key of Turris MOX';

CREATE TABLE programmer_state (
	id serial PRIMARY KEY,
	hostname text NOT NULL,
	rtools_git text NOT NULL,
	moximager_git text NOT NULL,
	moximager_hash varchar(64) NOT NULL,
	secure_firmware varchar(64) NOT NULL,
	uboot varchar(64) NOT NULL,
	rescue varchar(64) NOT NULL,
	dtb varchar(64) NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN programmer_state.hostname IS 'Hostname of programmer';
COMMENT ON COLUMN programmer_state.rtools_git IS 'git describe of used rtools-gui repository';
COMMENT ON COLUMN programmer_state.moximager_git IS 'git describe of used mox-imager repository';
COMMENT ON COLUMN programmer_state.moximager_hash IS 'sha256sum of used mox-imager binary';
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
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN runs.programmer_id IS 'ID of used programmer board';
COMMENT ON COLUMN runs.steps IS 'Planned steps (not executed ones those are in steps table)';

CREATE TABLE run_results (
	id bigint PRIMARY KEY REFERENCES runs (id),
	success boolean NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN run_results.success IS 'If run reached last step without error or warning';

CREATE TABLE steps (
	id bigserial PRIMARY KEY,
	step_name text NOT NULL,
	run bigint REFERENCES runs (id),
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN steps.step_name IS 'Name of step it self. Used to identify this step.';

CREATE TABLE step_results (
	id bigint PRIMARY KEY REFERENCES steps (id),
	success boolean NOT NULL,
	message text,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN step_results.success IS 'Boolean if step passed successfully.';
COMMENT ON COLUMN step_results.message IS 'Error or warning message produced by this step';

CREATE TABLE sets (
	id bigserial PRIMARY KEY,
	type text NOT NULL,
	add_time timestamp NOT NULL DEFAULT current_timestamp
);
COMMENT ON COLUMN sets.type IS 'Set type/name identifier.';

CREATE TABLE set_boards (
	board bigint PRIMARY KEY REFERENCES boards (serial),
	set bigint REFERENCES sets (id)
);
