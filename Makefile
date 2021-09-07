all:
	@echo "usage: make <options> \nuse 'make help' to find out more."

help:
	@echo "options:\n\thelp: get help on the makefile"
	@echo "\t\run: run project in a docker container"
	@echo "\t\local: run project localy"
	@echo "\ttest: run ci/cd pipeline tasks"
	@echo "\tinstall: install all required packages for the project"
	@echo "\tstart_broker: start redis as the celery broker"
	@echo "\tstop_broker: stop the celery broker"
	@echo "\trestart_broker: restart the celery broker"
	@echo "\tstart_celery: start a celery worker"
	@echo "\tstart_celerybeat: start the celery beat service"

run:
	docker-compose up --build

local: start_broker start_celery
	python manage.py runserver

test: 
	test-migrations test-pylint

test-migrations:
	python manage.py makemigrations --check --dry-run

test-pylint:
	find . -type f -name "*.py" | grep -vE "migrations|^./venv|^./cache|^./lib|^./media" | xargs pylint

install:
	pip install -r requirements.txt

start_broker:
	docker run --name broker -d -p6379:6379 redis:alpine

stop_broker:
	docker stop broker

restart_broker:
	docker start broker

start_celery:
	celery -A data_platform worker -l INFO --detach

start_celerybeat:
	celery -A data_platform beat