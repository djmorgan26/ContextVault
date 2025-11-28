.PHONY: help install dev test lint format migrate clean

help:
	@echo "ContextVault Backend - Available Commands"
	@echo "=========================================="
	@echo "make install    - Install dependencies in virtual environment"
	@echo "make dev        - Start development server with hot reload"
	@echo "make test       - Run all tests with coverage"
	@echo "make lint       - Run Ruff linter"
	@echo "make format     - Format code with Ruff"
	@echo "make migrate    - Run database migrations"
	@echo "make clean      - Remove cache and temporary files"

install:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

dev:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	./venv/bin/pytest tests/ --cov=app --cov-report=term-missing --cov-report=html -v

lint:
	./venv/bin/ruff check .

format:
	./venv/bin/ruff format .
	./venv/bin/ruff check --fix .

migrate:
	./venv/bin/alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	./venv/bin/alembic revision --autogenerate -m "$$msg"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
