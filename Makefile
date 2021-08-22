BUILD_DIR=build

all:
	@echo "usage: make <options> \nuse 'make help' to find out more."

help:
	@echo "options:\n\thelp: get help on the makefile\n\ttest: run ci/cd pipeline tasks"
	@echo "\tinstall: install all required packages for the project"

test: 
	find . -type f -name "*.py" | xargs pylint --rcfile=.pylintrc --output-format=text --exit-zero 
	python3 manage.py makemigrations --check

install:
	pip install -r requirements.txt
	