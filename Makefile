# Makefile for development.
# See INSTALL and docs/dev.txt for details.
ROOT_DIR = $(shell pwd)
WGET = wget
PROJECT = $(shell python -c "import setup; print setup.NAME")
DIECUTTER_PUBLIC_API = http://diecutter.io/api
DIECUTTER_LOCAL_API = http://localhost:8106


configure:
	mkdir -p $(ROOT_DIR)/etc
	wget -O etc/diecutter.ini --post-data "template_dir=$(ROOT_DIR)/demo/templates" $(DIECUTTER_PUBLIC_API)/diecutter.ini


develop:
	pip install -r tests-requirements.pip
	rm -rf $(ROOT_DIR)/*.egg

clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info


maintainer-clean: distclean

serve:
	pserve $(ROOT_DIR)/etc/diecutter.ini --reload


test: test-app test-pep8 test-documentation


test-app:
	mkdir -p var/test
	nosetests --config=etc/nose.cfg --config=etc/nose-app.cfg $(PROJECT) tests


test-pep8:
	flake8 $(PROJECT) tests


test-documentation:
	nosetests -c $(ROOT_DIR)/etc/nose.cfg sphinxcontrib.testbuild.tests


documentation: sphinx-doctest sphinx-apidoc sphinx-html


sphinx-doctest: sphinx-apidoc-clean
	make --directory=docs clean doctest


# Remove auto-generated API documentation files.
# Files will be restored during sphinx-build, if "autosummary_generate" option
# is set to True in Sphinx configuration file.
sphinx-apidoc-clean:
	find docs/framework/api/ -type f \! -name "index.txt" -delete
	echo -e "Modules\n=======" > $(ROOT_DIR)/docs/framework/api/modules.txt


sphinx-apidoc: sphinx-apidoc-clean
	rm $(ROOT_DIR)/docs/framework/api/modules.txt
	sphinx-apidoc --suffix txt --output-dir $(ROOT_DIR)/docs/framework/api $(PROJECT)


sphinx-html:
	mkdir -p docs/_static
	make --directory=docs clean html


generate-documentation:
	curl -X POST -H "Content-Type: text/plain" --data-binary "@demo/presets/sphinx-docs.cfg" $(DIECUTTER_LOCAL_API)/sphinx-docs/ > var/sphinx-docs.zip
	unzip -d docs/ var/sphinx-docs.zip
	rm var/sphinx-docs.zip


release:
	pip install zest.releaser
	fullrelease
