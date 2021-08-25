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


def validate_schedule_interval(value):
    if value < timedelta(minutes=1):
        raise ValidationError(_('Schedule interval should be more than 1 minute.'))


class WorkflowSchedule(models.Model):
    workflow = models.OneToOneField(Workflow, on_delete=models.CASCADE, related_name='schedule')

    start_time = models.DateTimeField()
    schedule_interval = models.DurationField(validators=[validate_schedule_interval])

    next_run_time = models.DateTimeField(blank=True, null=True)

    paused = models.BooleanField(default=False, db_index=True)
