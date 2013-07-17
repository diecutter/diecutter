# Makefile for development.
# See INSTALL and docs/dev.txt for details.
SHELL = /bin/bash
ROOT_DIR = $(shell pwd)
BIN_DIR = $(ROOT_DIR)/bin
DATA_DIR = $(ROOT_DIR)/var
WGET = wget
BUILDOUT_CFG = $(ROOT_DIR)/etc/buildout.cfg
BUILDOUT_DIR = $(ROOT_DIR)/lib/buildout
BUILDOUT_VERSION = 2.2.0
BUILDOUT_BOOTSTRAP_URL = https://raw.github.com/buildout/buildout/$(BUILDOUT_VERSION)/bootstrap/bootstrap.py
BUILDOUT_BOOTSTRAP = $(BUILDOUT_DIR)/bootstrap.py
BUILDOUT_BOOTSTRAP_ARGS = -c $(BUILDOUT_CFG) --version=$(BUILDOUT_VERSION) buildout:directory=$(ROOT_DIR)
BUILDOUT = $(BIN_DIR)/buildout
BUILDOUT_ARGS = -N -c $(BUILDOUT_CFG) buildout:directory=$(ROOT_DIR)
VIRTUALENV_DIR = $(ROOT_DIR)/lib/virtualenv
PIP = $(VIRTUALENV_DIR)/bin/pip
NOSE = $(BIN_DIR)/nosetests
PYTHON = $(VIRTUALENV_DIR)/bin/python
PROJECT = $(shell $(PYTHON) -c "import setup; print setup.NAME")
DIECUTTER_PUBLIC_API = http://diecutter.alwaysdata.net/api
DIECUTTER_LOCAL_API = http://localhost:8106


configure:
	mkdir -p $(ROOT_DIR)/etc
	wget -O etc/diecutter.ini --post-data "template_dir=$(ROOT_DIR)/demo/templates" $(DIECUTTER_PUBLIC_API)/diecutter.ini


develop: buildout


py27:
	virtualenv --no-site-packages $(VIRTUALENV_DIR)
	$(PIP) install pip==1.3.1
	$(PIP) install setuptools==0.8


buildout: py27
	if [ ! -d $(BUILDOUT_DIR) ]; then mkdir -p $(BUILDOUT_DIR); fi
	if [ ! -f $(BUILDOUT_BOOTSTRAP) ]; then wget -O $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_URL); fi
	if [ ! -x $(BUILDOUT) ]; then $(PYTHON) $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_ARGS); fi
	$(BUILDOUT) $(BUILDOUT_ARGS)


clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info


maintainer-clean: distclean
	rm -rf $(BIN_DIR)/
	rm -rf $(ROOT_DIR)/lib/


serve:
	$(BIN_DIR)/pserve $(ROOT_DIR)/etc/diecutter.ini --reload


test: test-app test-pep8 test-documentation


test-app:
	$(NOSE) --config=etc/nose.cfg $(PROJECT)
	rm $(ROOT_DIR)/.coverage


test-pep8:
	$(BIN_DIR)/flake8 $(PROJECT)


test-documentation:
	$(NOSE) -c $(ROOT_DIR)/etc/nose.cfg sphinxcontrib.testbuild.tests
	rm $(ROOT_DIR)/.coverage


documentation: sphinx-apidoc sphinx-html


# Remove auto-generated API documentation files.
# Files will be restored during sphinx-build, if "autosummary_generate" option
# is set to True in Sphinx configuration file.
sphinx-apidoc-clean:
	find docs/framework/api/ -type f \! -name "index.txt" -delete


sphinx-apidoc: sphinx-apidoc-clean
	$(BIN_DIR)/sphinx-apidoc --suffix txt --output-dir $(ROOT_DIR)/docs/framework/api $(PROJECT)


sphinx-html:
	if [ ! -d docs/_static ]; then mkdir docs/_static; fi
	make --directory=docs clean html doctest


generate-documentation:
	curl -X POST -H "Content-Type: text/plain" --data-binary "@demo/presets/sphinx-docs.cfg" $(DIECUTTER_LOCAL_API)/sphinx-docs/ > var/sphinx-docs.zip
	unzip -d docs/ var/sphinx-docs.zip
	rm var/sphinx-docs.zip


release:
	$(BIN_DIR)/fullrelease
