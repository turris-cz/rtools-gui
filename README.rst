Router Tools GUI
================

This piece of software is designed to be used for Turris Omnia provisioning.

Requirements
------------

- PyQt5

  - `python-pyqt5`
  - `libqt5sql5-psql`
  - `python-pyqt5.qtsql`
  - `python-pyqt5.qtserialport`

- pexpect

  - `python-pexpect`

Howto run it
------------

``./rtools-gui.py``

``./rtools-gui.py -t`` (tests only)

``./rtools-gui.py -s`` (steps only)

Settings
--------

By default the settings are included in for of a python file (`settings.omnia`).
To load custom settings you cat simply set env variable `RTOOLS_SETTINGS`::

    RTOOLS_SETTINGS='settings.custom' ./rtools-gui.py

Variables
_________

``DB``
  Specifies the db connection.

``WORKFLOW_STEPS_MODULE = 'workflow.steps.omnia'``
  Sets which steps shall be performed during the board awakening.

``WORKFLOW_TESTS_MODULE = 'workflow.tests.omnia'``
  Sets which tests shall be performed when the board is awaken.

``SCRIPTS``
  Paths to the scripts which shall be executed during the steps/tests.

``SERIAL_CONSOLE``
  Specifies parameters of a serial console devices which are connected during the steps/tests.

``LOG_APP_FILE = '/var/log/programmer/application.log'``
  Path to the application log.

``LOG_ROUTERS_DIR = '/var/log/programmer/runs/'``
  Directory where outputs of individual steps/tests batches should be placed.

``DB_RECOVER_QUERY_FILE = '~/recover-queries.json'``
  If a connection to db fails during the steps/tests the failed db queries are placed here.
  This file is read after the application starts and the queries are written into db.

``BACKUP_SCRIPT = 'backup_log.sh'``
  Path to a backup script. This script is use do backup application logs well as individual
  tests/steps outputs.
