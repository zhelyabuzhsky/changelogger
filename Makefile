RUN := run --rm
DOCKER_COMPOSE := docker compose -f dev/docker-compose.yml
DOCKER_COMPOSE_RUN := ${DOCKER_COMPOSE} $(RUN)

default: test

install:
	pip install -rrequirements.txt

test:
	pytest changelogs/

migrate:
	./manage.py migrate

assets:
	./manage.py collectstatic --noinput

compose-build:
	${DOCKER_COMPOSE} build web

compose-install:
	${DOCKER_COMPOSE_RUN} app make install

compose-migrate:
	${DOCKER_COMPOSE_RUN} app make migrate

compose-web:
	${DOCKER_COMPOSE_RUN} --service-ports web

compose-prepare: compose-build compose-install compose-migrate