all:
	@echo "usage: make <options> \nuse 'make help' to find out more."

help:
	@echo "options:\n\thelp: get help on the makefile\n\ttest: run ci/cd pipeline tasks"
	@echo "\tinstall: install all required packages for the project"

test: test-migrations test-pylint

test-migrations: 
	python manage.py makemigrations --check --dry-run

test-pylint:
	find . -type f -name "*.py" | grep -vE "migrations|^./venv|^./cache" | xargs pylint

install:
	pip install -r requirements.txt
