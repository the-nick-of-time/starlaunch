sources = $(wildcard starlaunch/*.py)
version := $(shell poetry version --short)

dist/StarLaunch dist/Starlaunch.exe: $(sources) icon.ico
	poetry run pyinstaller --onefile --noconsole --paths=starlaunch --name=StarLaunch --icon=icon.ico starlaunch/main.py

dist/starlaunch-$(version).tar.gz dist/starlaunch-$(version)-py3-none-any.whl: $(sources)
	poetry build

icon.ico: icon.svg
	for dim in 16 32 64 256 ; do inkscape --export-filename="icon_$$dim.png" --export-width="$$dim" --export-height="$$dim" $< ; done
	convert icon_*.png icon.ico
