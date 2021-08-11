import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        commands = "docker run --name broker -d -p6379:6379 redis"
        subprocess.check_output(commands, shell=True)
