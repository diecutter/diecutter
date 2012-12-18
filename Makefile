ROOT_DIR = $(shell pwd)
VIRTUALENV = virtualenv
VIRTUALENV_DIR = $(ROOT_DIR)/lib/virtualenv
BIN_DIR = $(VIRTUALENV_DIR)/bin
PIP = $(BIN_DIR)/pip

virtualenv:
	if [ ! -d $(VIRTUALENV_DIR) ]; then mkdir -p $(VIRTUALENV_DIR); fi
	if [ ! -x $(PIP) ]; then $(VIRTUALENV) $(VIRTUALENV_DIR); fi

develop: virtualenv
	$(PIP) install -e $(ROOT_DIR)

serve:
	$(BIN_DIR)/pserve diecutter.ini --reload
