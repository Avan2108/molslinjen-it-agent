.PHONY: dev test lint format install clean

# Development server
dev:
	uvicorn app.main:app --reload --port 8000

# Run tests
test:
	pytest tests/ -v --cov=app --cov-report=term-missing

# Run tests with HTML coverage report
test-cov:
	pytest tests/ -v --cov=app --cov-report=html

# Linting
lint:
	ruff check app/ tests/
	mypy app/

# Format code
format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

# Install dependencies
install:
	pip install -r requirements.txt

# Create virtual environment and install
setup:
	python -m venv .venv
	.venv\Scripts\activate && pip install -r requirements.txt

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
