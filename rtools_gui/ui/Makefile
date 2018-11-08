UI = mainwindow programmer
UI_PY_FILES = $(patsubst %,%.py,$(UI))

all: icons.py $(UI_PY_FILES)

icons.py: icons.qrc
	pyrcc5 $< -o $@

$(UI_PY_FILES): %.py: %.ui
	pyuic5 --import-from=. --resource-suffix= $< -o $@

clean:
	rm -f icons.py $(UI_PY_FILES)
