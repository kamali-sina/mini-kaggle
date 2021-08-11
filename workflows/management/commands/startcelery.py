"""
to configure celery:
    make sure to be update with 'requirements.txt'
    also make sure to have applied migrations with 'python manage.py migrate django_celery_results'
    then, run 'python manage.py startbroker' and 'python manage.py startcelery'

now you are ready to runserver!
"""

import subprocess

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        commands = "celery -A data_platform worker -l INFO;"
        subprocess.check_output(commands, shell=True)
