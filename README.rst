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
  - `python3-ftdi1`
  - `libftdi1`
  - `librsvg2-dev`

- For MOX Imager

  - `build-essential`
  - `libssl1.0-dev`

Virtual environment
-------------------

Make sure to create `venv` dependent on `--system-site-packages`
(`python3-ftdi1`, `librsvg2-dev`) won't make the connection

- ``python -m venv [desired path] --system-site-packages``

Preparation
-----------

To compile neccessary files for ``mox-imager`` make sure you have initialized
submodule

- ``git submodule update --init --recursive``

Howto run it
------------

``make -C mox-imager && ./rtools-gui.py``

Settings
--------

Settings are in INI format and automatically located in either `./rtools-gui.conf`
or `~/.rtools-gui.conf`. This repository contains an example for configuration
file.
