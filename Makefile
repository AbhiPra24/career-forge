.PHONY: install install-all install-cli install-skills install-mcp uninstall test test-cov lint format clean mcp-run

PYTHON ?= python3

# Package Installation
install:
	$(PYTHON) -m pip install -e ".[dev]" || $(PYTHON) scripts/install.py --cli-only

# Automated Full System & Agent Integration
install-all:
	$(PYTHON) scripts/install.py

install-cli:
	$(PYTHON) scripts/install.py --cli-only

install-skills:
	$(PYTHON) scripts/install.py --skills-only

install-mcp:
	$(PYTHON) scripts/install.py --mcp-only

uninstall:
	$(PYTHON) scripts/install.py --uninstall

# Testing & Quality Gates
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover tests

test-cov:
	PYTHONPATH=src $(PYTHON) -m pytest tests/ --cov=career_forge --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check src/ tests/

format:
	$(PYTHON) -m ruff format src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# MCP Server Runner
mcp-run:
	PYTHONPATH=src $(PYTHON) -m career_forge.mcp_server
