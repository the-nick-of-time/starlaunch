sources = $(wildcard starlaunch/*.py)
version := $(shell poetry version --short)

dist/StarLaunch dist/Starlaunch.exe: $(sources)
	poetry run pyinstaller --onefile --noconsole --paths=starlaunch --name=StarLaunch starlaunch/main.py

dist/starlaunch-$(version).tar.gz dist/starlaunch-$(version)-py3-none-any.whl: $(sources)
	poetry build
