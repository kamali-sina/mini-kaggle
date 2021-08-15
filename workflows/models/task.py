from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from workflows.models.workflow import Workflow


class Task(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

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
