ROOT_DIR = $(shell pwd)
VIRTUALENV = virtualenv
VIRTUALENV_DIR = $(ROOT_DIR)/lib/virtualenv
BIN_DIR = $(VIRTUALENV_DIR)/bin
PIP = $(BIN_DIR)/pip
DIECUTTER_PUBLIC_API = http://diecutter.alwaysdata.net


virtualenv:
	if [ ! -d $(VIRTUALENV_DIR) ]; then mkdir -p $(VIRTUALENV_DIR); fi
	if [ ! -x $(PIP) ]; then $(VIRTUALENV) $(VIRTUALENV_DIR); fi


configure:
	mkdir -p $(ROOT_DIR)/etc
	wget -O etc/diecutter.ini --post-data "template_dir=$(ROOT_DIR)/demo/templates" $(DIECUTTER_PUBLIC_API)/diecutter.ini


develop: virtualenv configure
	$(PIP) install -e $(ROOT_DIR)


serve:
	$(BIN_DIR)/pserve $(ROOT_DIR)/etc/diecutter.ini --reload
