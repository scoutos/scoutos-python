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
	@poetry install --no-root

setup: clean install-deps

teardown: clean

.PHONY: test
test: ## Run a test of the example
	@echo "Testing the example..."
	@poetry run python main.py "What should I do today?"
