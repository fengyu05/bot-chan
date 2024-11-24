include makefiles/help.mk
include makefiles/docker.mk
include makefiles/docker-ci.mk
include makefiles/poetry.mk
include makefiles/alembic.mk

DB_APP=api

slack-server: requirements.txt ## start slack server
	docker compose up --build server-slack

discord-server: requirements.txt ## start discord server
	docker compose up --build server-discord

debug-server: requirements.txt ## start app server with debug mode
	docker compose up --build server-debug

api-server: requirements.txt ## start app server
	docker compose up --build api

test: docker-test  ## Test