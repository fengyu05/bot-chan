.PHONY: server server-dev test lint fmt shell bash help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@echo "===== All tasks ====="
	@cat $(MAKEFILE_LIST) | python -c "$$PRINT_HELP_PYSCRIPT"

build:  ## build image
	docker compose build

server:  ## start prod server
	docker compose up --build app

server-dev:  ## start dev server
	docker compose up --build app-dev

shell: # shell backend
	docker compose up -d --build shell

bash: shell  ## Connect to a bash within the docker image
	docker compose exec shell bash

test: ## Run unit tests
	docker compose up --build test

## CI tool targets below
c-build:  ## Build CI image
	docker compose build

ci-shell: # Create CI shell backend
	docker compose -f docker-compose-ci.yml up --build -d shell

ci-bash: ci-shell  ## Connect to a bash within the tool image(faster), for running task like `poetry lock`
	docker compose -f docker-compose-ci.yml exec shell bash

lint:  ## Lint the code folder
	docker compose -f docker-compose-ci.yml up --build lint

fmt:  ## Apply python formater(will edit the code)
	CURRENT_UID=$$(id -u):$$(id -g) docker compose -f docker-compose-ci.yml up --build fmt


