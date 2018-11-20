Router Tools GUI
================

This piece of software is designed to be used for Turris Mox provisioning.

Requirements
------------

- For application it self

  - `python3-pyqt5`
  - `python3-pexpect`
  - `python3-psycopg2`
  - `python3-libftdi1`

- For MOX Imager

  - `build-essential`
  - `libssl-dev`


Howto run it
------------

``make -C mox-imager && ./rtools-gui.py``

Settings
--------

Settings are in INI format and automatically located in either `./rtools-gui.conf`
or `~/rtools-gui.conf`. This repository contains an example for configuration
file.
