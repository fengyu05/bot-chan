include makefiles/help.mk
include makefiles/docker.mk
include makefiles/docker-ci.mk
include makefiles/poetry.mk

.PHONY: app app-debug

server: requirements.txt ## start app server
	docker compose up --build app

server-debug: requirements.txt ## start app server with debug mode
	docker compose up --build app-debug

api-server: requirements.txt ## start app server
	docker compose up --build api db

test: docker-test  ## Test