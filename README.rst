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

- prctl

  - `python-prctl`

Howto run it
------------

``./rtools-gui.py``

``./rtools-gui.py -t`` (tests only)

``./rtools-gui.py -s`` (steps only)

How to run it in offline mode 
-----------------------------

Offline mode doesn't use database and calls from/to database are mocked.

Use provided custom settings ``omnia_offline`` ::

    RTOOLS_SETTINGS='settings.omnia_offline' ./rtools-gui.py

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

``PATHS``
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


Querying database
-----------------

If you want to get all successfully processed routers you can simply::

    SELECT * FROM good_routers;

If you want to list info about steps for a specific router you can::

    SELECT * FROM router_steps('38654706684');

Same for the tests::

    SELECT * FROM router_tests('38654706684');


Writing steps / tests
---------------------

To write a custom steps / tests you need to understand a underlying logic a bit.

Running
_______
After the barcode is scanned db is checked for records about the serial number.
It checks whether all steps are passed (`WORKFLOW_STEPS_MODULE`) if not the remains steps are planned for the next run.
If all steps are passed the tests (`WORKFLOW_TESTS_MODULE`) could be planned.
Once a step passes it can't be run again.
If step fails the execution won't continues.

Runner
______
Is resposible for running the planned tests / steps.
It is listens for signels send from the tests / steps.
It could trigger some actions (e.g. update progress bar, store firmware).
The order of the execution depends on the `WORKFLOW` variable of the tests / steps module.

Steps / Tests
_____________
Steps and tests are defined here::

  workflow/

The steps and tests are using the same superclass.
It contains some commonf functions and it handles dome basic logic.

The only difference between a test and a step is that test class contains ``continueOnFailure = True`` definition.

A sample test class looks something like this::

    class Sample(Base):
        _name = 'SAMPLE'

        def __init__(self, param1, param2, ...):
            self.param1 = param1
            self.param2 = param2
            ...

        def createWorker(self):
            return self.Worker(self.param1, self.param2, ...)

        class Worker(BaseWorker):
            def __init__(self, param1, param2, ...):
                super(Sample.Worker, self).__init__()
                self.param1 = param1
                self.param2 = param2
                ...

            def perform(self):
                ...
                return True

Note the ``Worker`` class is a ``QObject`` which is moved to another ``QThread`` so it is not possible to communicate with e.g. ``Runner`` class directly.
You are only able to emit a signal.

When you want to display some instructions before the test / step is performed you can use this::

    class Sample(Base):
        _name = 'SAMPLE'

        @property
        def instructions(self):
            return """<b>TO THIS BEFORE RUNNING THE TEST</b>"""

To access a current settings variables you can simply do this::

    from application import settings
    settings.SERIAL_CONSOLE['router']['device']

Pexpect is used to check and wait for the output of the serial consoles.
Some of its calls are wrapped to have more reasonable output in logs or to avoid a redundant code.
See the example::

    def perform(self):
        exp = spawnPexpectSerialConsole(settings.SERIAL_CONSOLE['router']['device'])
        self.progress.emit(1)
        exp.sendline('ls -al')
        self.progress.emit(50)
        self.expect(exp, r'\.\.')
        self.progress.emit(100)

Mocking
_______

Sometimes during the development it can be useful to mock some functionality.
Note that some steps are irreversible and can't be repeated (atsha).

You can specify your own settings for that::

    RTOOLS_SETTINGS='settings.mock' ./rtools-gui.py

Where you can alter a path to a local script::

    PATHS = {
        'sample': {
            'path': 'mock/sample.sh'
        }
    }

Or mock the tester or router serial console output::

    SERIAL_CONSOLE = {
        'tester': {
            'device': "/dev/ttyTESTER",
            'baudrate': 115200,
            'mock': 'mock/sc_pipe_tester_mock.py',
        },
        'router': {
            'device': "/dev/ttyROUTER",
            'baudrate': 115200,
            'mock': 'mock/sc_pipe_router_mock.py.py',
        },
    }

Note that the sample mock scripts / programs are not complete and you'd need to add some parts.
