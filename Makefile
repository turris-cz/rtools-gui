UI = window programmer
UI_PY_FILES = $(patsubst %,ui/%.py,$(UI))

all: qrc/icons.py $(UI_PY_FILES)

qrc/icons.py: qrc/icons.qrc
	pyrcc5 $< -o $@

$(UI_PY_FILES): %.py: %.ui
	pyuic5 --import-from=qrc --resource-suffix= $< -o $@

clean:
	rm -f qrc/icons.py $(UI_PY_FILES)
