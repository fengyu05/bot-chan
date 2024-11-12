include makefiles/help.mk
include makefiles/docker.mk
include makefiles/docker-ci.mk
include makefiles/poetry.mk

.PHONY: app app-debug

app: requirements.txt ## start app server
	docker compose up --build app

app-debug: requirements.txt ## start app server with debug mode
	docker compose up --build app-debug

test: docker-test  ## Test