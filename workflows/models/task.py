import datetime

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from workflows.models.workflow import Workflow
from notifications.models import NotificationSource
from datasets.models import Dataset


class Task(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    accessible_datasets = models.ManyToManyField(Dataset)

    notification_source = models.ForeignKey(NotificationSource, on_delete=models.SET_NULL, null=True)
    alert_on_failure = models.BooleanField(default=False)

    timeout = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.name


class TaskExecution(models.Model):
    class StatusChoices(models.TextChoices):
        RUNNING = "R", _("Running")
        SUCCESS = "S", _("Success")
        FAILED = "F", _("Failed")
        PENDING = "P", _("Pending")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING)
