# Reference card for usual actions in development environment.
#
# For standard installation of diecutter, see INSTALL.
# For details about diecutter's development environment, see CONTRIBUTING.rst.
#
WGET = wget
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
	pip install -r tests-requirements.pip
	rm -rf *.egg

#: clean - Basic cleanup, mostly temporary files.
clean:
	find . -name "*.pyc" -delete


#: distclean - Remove local builds, such as *.egg-info.
distclean: clean
	rm -rf *.egg-info


#: maintainer-clean - Remove almost everything that can be re-generated.
maintainer-clean: distclean


#: serve - Run local diecutter server.
serve:
	pserve etc/diecutter.ini --reload


#: test - Run test suites.
test: test-app test-pep8


test-app:
	mkdir -p var/test
	nosetests --config=etc/nose.cfg --config=etc/nose-app.cfg $(PROJECT) tests


test-pep8:
	flake8 $(PROJECT) tests


test-documentation:
	nosetests -c etc/nose.cfg sphinxcontrib.testbuild.tests


#: documentation - Build documentation (Sphinx, README, ...)
documentation: sphinx-doctest sphinx-apidoc sphinx-html


sphinx-doctest: sphinx-apidoc-clean
	make --directory=docs clean doctest


# Remove auto-generated API documentation files.
# Files will be restored during sphinx-build, if "autosummary_generate" option
# is set to True in Sphinx configuration file.
sphinx-apidoc-clean:
	find docs/framework/api/ -type f \! -name "index.txt" -delete
	echo -e "Modules\n=======" > docs/framework/api/modules.txt


sphinx-apidoc: sphinx-apidoc-clean
	rm docs/framework/api/modules.txt
	sphinx-apidoc --suffix txt --output-dir docs/framework/api $(PROJECT)


sphinx-html:
	mkdir -p docs/_static
	make --directory=docs clean html


generate-documentation:
	curl -X POST -H "Content-Type: text/plain" --data-binary "@demo/presets/sphinx-docs.cfg" $(DIECUTTER_LOCAL_API)/sphinx-docs/ > var/sphinx-docs.zip
	unzip -d docs/ var/sphinx-docs.zip
	rm var/sphinx-docs.zip


#: release - Tag and push to PyPI.
release:
	pip install zest.releaser
	fullrelease
