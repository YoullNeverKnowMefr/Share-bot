PYTHON ?= python
POETRY ?= poetry

.PHONY: install dev up down migrate lint test fmt

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

dev:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .[dev]

up:
	docker compose up -d

down:
	docker compose down

migrate:
	PYTHONPATH=./src alembic upgrade head

lint:
	ruff check .

test:
	pytest
