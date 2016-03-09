all: qrc/icons.py ui/mainwindow.py

qrc/icons.py: qrc/icons.qrc
	pyrcc5 $< -o $@

ui/mainwindow.py: ui/mainwindow.ui
	pyuic5 $< -o $@
