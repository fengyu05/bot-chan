include makefiles/help.mk
include makefiles/docker.mk
include makefiles/docker-lint.mk
include makefiles/docker-ci.mk
include makefiles/poetry.mk

.PHONY: app app-debug

app:  ## start app server
	docker compose up --build app

app-debug:  ## start app server with debug mode
	docker compose up --build app-debug

test: docker-compose-test  ## Test
lint: docker-compose-lint  ## Lint
fmt: docker-compose-fmt  ## Fmt
