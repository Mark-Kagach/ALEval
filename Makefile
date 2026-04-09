.PHONY: install install-dev install-swe install-analysis test test-unit test-integration lint format check clean

# Install targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pre-commit install

install-swe:
	pip install -e ".[swe]"

install-analysis:
	pip install -e ".[analysis]"

# Test targets
test:
	pytest tests/ -v -m "not docker and not slow"

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m "not docker"

test-all:
	pytest tests/ -v

# Lint and format
lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

check: lint
	ruff format --check src/ tests/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
