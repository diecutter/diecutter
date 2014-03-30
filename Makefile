# Reference card for usual actions in development environment.
#
# For standard installation of diecutter, see INSTALL.
# For details about diecutter's development environment, see CONTRIBUTING.rst.
#
PIP = pip
RELEASE = fullrelease
TOX = tox
WGET = wget
PSERVE = pserve
PROJECT = $(shell python -c "import setup; print setup.NAME")
DIECUTTER_PUBLIC_API = http://diecutter.io/api
DIECUTTER_LOCAL_API = http://localhost:8106


.PHONY: all help configure develop clean distclean maintainer-clean serve test documentation release


# Default target. Does nothing.
all:
	@echo "Reference card for usual actions in development environment."
	@echo "Nothing to do by default."
	@echo "Try 'make help'."


#: help - Display callable targets.
help:
	@echo "Reference card for usual actions in development environment."
	@echo "Here are available targets:"
	@egrep -o "^#: (.+)" [Mm]akefile  | sed 's/#: /* /'


#: configure - Generate etc/diecutter.ini configuration file.
configure:
	mkdir -p etc
	wget -O etc/diecutter.ini --post-data "template_dir=$(shell pwd)/demo/templates" $(DIECUTTER_PUBLIC_API)/diecutter.ini


#: develop - Install minimal development utilities (tox, Sphinx, ...).
develop:
	$(PIP) install -r tests-requirements.pip


#: clean - Basic cleanup, mostly temporary files.
clean:
	find . -name "*.pyc" -delete


#: distclean - Remove local builds, such as *.egg-info.
distclean: clean
	rm -rf *.egg
	rm -rf *.egg-info


#: maintainer-clean - Remove almost everything that can be re-generated.
maintainer-clean: distclean
	rm -rf bin/
	rm -rf lib/
	rm -rf build/
	rm -rf dist/
	rm -rf .tox/


#: serve - Run local diecutter server.
serve:
	$(PSERVE) etc/diecutter.ini --reload


#: test - Run test suites.
test:
	$(TOX)


#: documentation - Build documentation (Sphinx, README, ...)
documentation: sphinx readme


sphinx:
	$(TOX) -e sphinx


#: readme - Build standalone documentation files (README, CONTRIBUTING...).
readme:
	$(TOX) -e readme


generate-documentation:
	curl -X POST -H "Content-Type: text/plain" --data-binary "@demo/presets/sphinx-docs.cfg" $(DIECUTTER_LOCAL_API)/sphinx-docs/ > var/sphinx-docs.zip
	unzip -d docs/ var/sphinx-docs.zip
	rm var/sphinx-docs.zip


#: release - Tag and push to PyPI.
release:
	$(TOX) -e release
