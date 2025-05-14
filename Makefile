# Determine the Python command (python or python3)
PYTHON := $(shell command -v python3 || command -v python)

# Setup project
setup:
	$(PYTHON) -m venv env
	$(PYTHON) -m pip install -r requirements.txt
