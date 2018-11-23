import os
import argparse
import configparser
from . import report


class Configs:
    "Configuration handler and arguments parser all at once"
    _DEF_CONFIG = [
        "/etc/rtools-gui.conf",
        "~/.config/rtools-gui.conf",
        "~/.rtools-gui.conf",
        "rtools-gui.conf",
        ]

    def __init__(self):
        # Parser arguments
        prs = argparse.ArgumentParser(description="Router programming tool - GUI")
        prs.add_argument('--no-otp', action='store_true', help="Skip OTP write")
        prs.add_argument('--config', '-c', action='store',
                         help="Use given config instead of default one.")
        prs.add_argument('--tmpdir', action='store',
                         help="Use given path to store temporally files.")
        self.args = prs.parse_args()
        # Load configuration files
        config_file = None
        if self.args.config is not None:
            cnf_path = os.path.expanduser(self.args.config)
            if os.path.isfile(cnf_path):
                config_file = cnf_path
            else:
                report.fail_exit("There is no such configuration file: " +
                                 str(self.args.config))
        if config_file is None:
            for def_config in self._DEF_CONFIG:
                cnf_path = os.path.expanduser(def_config)
                if os.path.isfile(cnf_path):
                    config_file = cnf_path
        self.config = configparser.ConfigParser()
        if config_file is not None:
            self.config.read(config_file)

    @property
    def trusted(self):
        """If we should run in trusted or untrusted mode. Difference is
        whatever OTP should be flashed and what image should be used.
        """
        return not self.args.untrusted

    @property
    def no_otp(self):
        """If we should write OTP even in untrusted mode"""
        return self.args.no_otp

    @property
    def tmp_dir(self):
        """Path to tmp directory"""
        tmp = self.args.tmpdir
        return tmp if tmp is None else "/tmp"

    def _db_value(self, name, default=None):
        if 'db' in self.config.sections() and name in self.config['db']:
            return self.config['db'][name]
        return default

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
