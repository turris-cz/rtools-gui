Router Tools GUI
================

This piece of software is designed to be used for Turris Mox provisioning.

Requirements
------------

- PyQt5

  - `python3-pyqt5`

- pexpect

  - `python3-pexpect`

- psycopg2

  - `python3-psycopg2`

- libftdi1

  - `python3-libftdi1`


Howto run it
------------

``./rtools-gui.py``

Settings
--------

Settings are in INI format and automatically located in either `./rtools-gui.conf`
or `~/rtools-gui.conf`. This repository contains an example for configuration
file.
