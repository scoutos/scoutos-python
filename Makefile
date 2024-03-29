.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


.PHONY: clean
clean: ## Remove virtual environment and cache
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "Removing cache..."
	@rm -rf ./__pycache__
	@rm -rf ./**/__pycache__


.PHONY: install-deps
install-deps: ## Install dependencies
	@echo "Installing dependencies..."
	@poetry install


.PHONY: check-all
check-all: check-smells check-format check-types ## Run all checks


.PHONY: check-smells
check-smells: ## Check code smells with Ruff
	@echo "Checking code smells..."
	@poetry run ruff check .


.PHONY: check-format
check-format: ## Check code formatting with Ruff
	@echo "Checking code formatting..."
	@poetry run ruff format . --check


.PHONY: check-types
check-types: ## Check types
	@echo "Checking types..."
	@poetry run mypy .


.PHONY: fix-format
fix-format: ## Fix code formatting with Ruff
	@echo "Fixing code formatting..."
	@poetry run ruff format .


.PHONY: fix-smells
fix-smells: ## Fix code smells with Ruff
	@echo "Fixing code smells..."
	@poetry run ruff check --fix .



.PHONY: test
test: ## Run unit tests
	@echo "Running unit tests..."
	@poetry run pytest --cov=scoutos --cov-report=term-missing --cov-fail-under=100
