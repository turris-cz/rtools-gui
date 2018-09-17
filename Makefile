all: qrc/icons.py ui/mainwindow.py

qrc/icons.py: qrc/icons.qrc
	pyrcc5 $< -o $@

ui/mainwindow.py: ui/mainwindow.ui
	pyuic5 --import-from=qrc --resource-suffix= $< -o $@

clean:
	rm qrc/icons.py ui/mainwindow.py
