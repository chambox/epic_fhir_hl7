# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
BLACK = $(VENV)/bin/black
PYTEST = $(VENV)/bin/pytest

# Targets
.PHONY: all clean install lint test run build

all: install lint test run build

install: 
	virtualenv $(VENV)
	chmod +x $(VENV)/bin/activate
	. $(VENV)/bin/activate
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

lint:
	. $(VENV)/bin/activate
	$(BLACK) .

test:
	. $(VENV)/bin/activate
	$(PYTEST)

clean:
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info

build:
	. $(VENV)/bin/activate
	$(PYTHON) setup.py sdist bdist_wheel
