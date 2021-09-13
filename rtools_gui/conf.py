import os
import argparse
import configparser
import ipaddress
from . import report


class Configs:
    "Configuration handler and arguments parser all at once"
    _DEF_CONFIG = [
        "/etc/rtools-gui.conf",
        "~/.config/rtools-gui.conf",
        "~/.rtools-gui.conf",
        "rtools-gui.conf",
    ]

    def __init__(self, argv):
        # Parser arguments
        prs = argparse.ArgumentParser(description="Router programming tool - GUI")
        prs.add_argument('--no-otp', action='store_true', help="Skip OTP write")
        prs.add_argument('--untrusted-firmware', action='store_true',
                         help="Use untrusted firmware instead of trusted one (in case of board without written OTP).")
        prs.add_argument('--config', '-c', action='store',
                         help="Use given config instead of default one.")
        prs.add_argument('--tmpdir', action='store',
                         help="Use given path to store temporally files.")
        self.args = prs.parse_args(argv)
        # Load configuration files
        config_file = None
        if self.args.config is not None:
            cnf_path = os.path.expanduser(self.args.config)
            if os.path.isfile(cnf_path):
                config_file = cnf_path
            else:
                report.fail_exit("There is no such configuration file: " + str(self.args.config))
        if config_file is None:
            for def_config in self._DEF_CONFIG:
                cnf_path = os.path.expanduser(def_config)
                if os.path.isfile(cnf_path):
                    config_file = cnf_path
        self.config = configparser.ConfigParser()
        if config_file is not None:
            self.config.read(config_file)

    def _fconf(self, section, option):
        "If set in configuration return string value"
        if section in self.config and option in self.config[section]:
            return self.config[section][option]
        return None

    def _fconf_bool(self, section, option):
        "Same as _fconf but does boolean transformation"
        if section in self.config and option in self.config[section]:
            return self.config[section].getboolean(option)
        return None

    @property
    def no_otp(self):
        """If we should write OTP or if we should skip it"""
        return self.args.no_otp or self._fconf_bool('rtools', 'no_otp')

    @property
    def use_untrusted(self):
        """If untrusted firmware should be used instead of trusted one"""
        return self.args.untrusted or self._fconf_bool('rtools', 'untrusted_firmware')

    @property
    def tmp_dir(self):
        """Path to tmp directory"""
        return self.args.tmpdir or self._fconf('rtools', 'tmpdir') or '/tmp'

    @property
    def suggest_test(self):
        """Number of failed tests before station test is suggested"""
        if 'rtools' in self.config.sections() and 'suggesttest' in self.config['rtools']:
            return self.config['rtools'].getint('suggesttest')
        return 3

    def _db_value(self, name, default=None):
        return self._fconf('db', name) or default

    @property
    def db_user(self):
        """Username to be used to connect to database"""
        return self._db_value('user')

    @property
    def db_password(self):
        """Username to be used to connect to database"""
        return self._db_value('password')

    @property
    def db_database(self):
        """Name of database to connect to"""
        return self._db_value('database', 'mox_boards')

    @property
    def db_host(self):
        """Target host for database"""
        return self._db_value('host')

    @property
    def db_port(self):
        """Port used to connect to given host to database"""
        return self._db_value('port')

    @property
    def tftp_dir(self):
        """Path to root directory of TFTP server"""
        if 'tftp' in self.config:
            return self.config['tftp'].get('dir', '/var/tftp')
        return None

    @property
    def tftp_ip(self):
        """IP address of TFTP server, that is IP of host system in same network as board is connected to."""
        return ipaddress.ip_address(self.config['tftp'].get('ip'))
