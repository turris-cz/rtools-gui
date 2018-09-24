MOX programming interface tool
==============================
To program Turris MOX we are using dedicated board (its documentation can be found
in doc directory). Hearth of this board is FT4232H. This chip contains four RS232
chips while two of them can be switched also to SPI or JTAG to name important
ones. Unfortunately this is not directly supported trough Linux. Thankfully FTDI
provides user-space library D2XX that can be used. Unfortunately this means that
simple Python script is not enough and because of that this programmer interfacing
tool was written.

Idea of this tool is to provide three interfaces:
* Control interface
* Serial console
* SPI

All interfaces are exported as named Unix sockets.

Dependencies
------------
* Somewhat new Linux (only tested on GNU user-space)
* libftd2xx

Compilation
-----------
To compile this tool you have to first run `bootstrap.sh`. Afterward you can use
standard `configure` and `make` approach.

Control interface
-----------------
Control interface provides message based communication intended for additional
tasks supported on top of other interfaces. Messages are lines of text and flow
either way although all of them are triggered 

Serial console
--------------

Serial Periphery Interface (SPI)
--------------------------------
