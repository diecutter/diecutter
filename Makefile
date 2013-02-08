ROOT_DIR = $(shell pwd)
BIN_DIR = $(ROOT_DIR)/bin
PYTHON = python
BUILDOUT_DIR = $(ROOT_DIR)/lib/buildout
BUILDOUT = $(BIN_DIR)/buildout
DIECUTTER_PUBLIC_API = http://diecutter.alwaysdata.net
NOSE = $(BIN_DIR)/nosetests


configure:
	mkdir -p $(ROOT_DIR)/etc
	wget -O etc/diecutter.ini --post-data "template_dir=$(ROOT_DIR)/demo/templates" $(DIECUTTER_PUBLIC_API)/diecutter.ini
	wget -O etc/buildout.cfg --post-data "" $(DIECUTTER_PUBLIC_API)/buildout/buildout.cfg
	wget -O etc/nose.cfg --post-data "package=diecutter" $(DIECUTTER_PUBLIC_API)/nose.cfg


develop: buildout


buildout:
	if [ ! -d $(BUILDOUT_DIR) ]; then \
		mkdir -p $(BUILDOUT_DIR); \
	fi
	if [ ! -f $(BUILDOUT_DIR)/bootstrap.py ]; then \
		wget -O $(BUILDOUT_DIR)/bootstrap.py https://raw.github.com/buildout/buildout/1.7.0/bootstrap/bootstrap.py; \
	fi
	if [ ! -x $(BUILDOUT) ]; then \
		$(PYTHON) $(BUILDOUT_DIR)/bootstrap.py --distribute -c etc/buildout.cfg buildout:directory=$(ROOT_DIR); \
	fi
	$(BUILDOUT) -N -c etc/buildout.cfg buildout:directory=$(ROOT_DIR)


clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info


maintainer-clean:
	rm -rf $(ROOT_DIR)/bin/ $(ROOT_DIR)/lib/


serve:
	$(BIN_DIR)/pserve $(ROOT_DIR)/etc/diecutter.ini --reload


test:
	$(NOSE) --config=etc/nose.cfg
	rm $(ROOT_DIR)/.coverage
