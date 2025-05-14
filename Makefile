# Determine the Python command (python or python3)
PYTHON := $(shell command -v python3 || command -v python)

# Setup project
setup:
	$(PYTHON) -m venv env --upgrade
	. env/bin/activate && \
	pip install -r requirements.txt
	tar -xzf geckodriver-v0.36.0-linux64.tar.gz -C build
	chmod +x build/geckodriver
