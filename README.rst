Router Tools GUI
================

This piece of software is designed to be used for Turris Mox provisioning.

Requirements
------------

- For application it self

  - `python3-pexpect`
  - `python3-psycopg2`
  - `python3-libftdi1`
  - `python3-yaml`
  - `python3-gi`
  - `python3-gi-cairo`
  - `gir1.2-gtk-3.0`

- For MOX Imager

  - `build-essential`
  - `libssl1.0-dev`


Howto run it
------------

``make -C mox-imager && ./rtools-gui.py``

Settings
--------

Settings are in INI format and automatically located in either `./rtools-gui.conf`
or `~/.rtools-gui.conf`. This repository contains an example for configuration
file.
