from datetime import timedelta
from django.db import models
from django.contrib import auth

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Workflow(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class WorkflowExecution(models.Model):
    class StatusChoices(models.TextChoices):
        """Different statuses of workflow execution, including:
         PENDING: the status in which the workflow execution is waiting for its first task dependency to run
         RUNNING: the status in which at least one task dependency of the workflow has started running
         SUCCESS: the status in which all the task dependencies of the workflow have been successfully run
         FAILED: the status in which at least one task dependency has failed
         """
        RUNNING = "R", _("Running")
        SUCCESS = "S", _("Success")
        FAILED = "F", _("Failed")
        PENDING = "P", _("Pending")

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


def validate_schedule_interval(value):
    if value < timedelta(minutes=1):
        raise ValidationError(_('Schedule interval should be more than 1 minute.'))


class WorkflowSchedule(models.Model):
    workflow = models.OneToOneField(Workflow, on_delete=models.CASCADE, related_name='schedule')

    start_time = models.DateTimeField()
    schedule_interval = models.DurationField(validators=[validate_schedule_interval])

    next_run_time = models.DateTimeField(blank=True, null=True)

    paused = models.BooleanField(default=False, db_index=True)
