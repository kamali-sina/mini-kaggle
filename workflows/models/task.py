from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)


class TaskExecution(models.Model):
    class StatusChoices(models.TextChoices):
        RUNNING = "R", _("Running")
        SUCCESS = "S", _("Success")
        FAILED = "F", _("Failed")
        PENDING = "P", _("Pending")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
