from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    class Status(models.TextChoices):
        NONE = 'N', _('None')
        RUNNING = 'R', _('Running')
        FAILED = 'F', _('Failed')
        STOPPED = 'S', _('Stopped')

    docker_image = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.NONE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
