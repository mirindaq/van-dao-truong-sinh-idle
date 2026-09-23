PYTHON ?= python3
BACKEND_DIR := backend
BACKEND_VENV := $(BACKEND_DIR)/.venv
BACKEND_PYTHON := $(BACKEND_VENV)/bin/python
BACKEND_DEPS := $(BACKEND_VENV)/.deps-installed

.PHONY: be db

be: $(BACKEND_DIR)/.env $(BACKEND_DEPS)
	cd $(BACKEND_DIR) && .venv/bin/python -m alembic upgrade head
	cd $(BACKEND_DIR) && .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db:
	docker compose up -d db

$(BACKEND_DIR)/.env: $(BACKEND_DIR)/.env.example
	cp $< $@

$(BACKEND_PYTHON):
	$(PYTHON) -m venv $(BACKEND_VENV)

$(BACKEND_DEPS): $(BACKEND_DIR)/pyproject.toml | $(BACKEND_PYTHON)
	$(BACKEND_PYTHON) -m pip install --upgrade pip
	$(BACKEND_PYTHON) -m pip install -e "./$(BACKEND_DIR)[dev]"
	touch $@
