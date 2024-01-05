.PHONY: server lint fmt index help
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
	docker-compose build

server:  ## start prod server
	docker-compose up --build app

server-dev:  ## start dev server
	docker-compose up --build app-dev

lint:  ## lint
	docker-compose -f docker-compose-ci.yml run lint

fmt:  ## apply py fmt
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-ci.yml run fmt

index:  ## create index
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-ci.yml run index

index-prod:  ## create index
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-ci.yml run index-prod