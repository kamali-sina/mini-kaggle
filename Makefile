all:
	@echo "usage: make <options> \nuse 'make help' to find out more."

help:
	@echo "options:\n\thelp: get help on the makefile\n\ttest: run ci/cd pipeline tasks"
	@echo "\tinstall: install all required packages for the project"

test: 
	find . -type f -name "*.py" | xargs pylint --exit-zero
	python3 manage.py makemigrations --check

install:
	pip install -r requirements.txt
	