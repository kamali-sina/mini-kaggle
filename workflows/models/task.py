from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from workflows.models.secret import Secret
from datasets.models import Dataset
from notifications.models import NotificationSource


def task_execution_log_file_directory_path(instance, filename):
    # pylint: disable=unused-argument
    return f"workflows/task_execution_logs/{filename}"


class Task(models.Model):
    class TaskTypeChoices(models.TextChoices):
        DOCKER = "DC", _("Docker")
        PYTHON = "PY", _("Python")

    DEFAULT_TYPE = TaskTypeChoices.DOCKER

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_variables = models.ManyToManyField(Secret, blank=True)
    accessible_datasets = models.ManyToManyField(Dataset, blank=True)

    notification_source = models.ForeignKey(NotificationSource, on_delete=models.SET_NULL, null=True, blank=True)
    alert_on_failure = models.BooleanField(default=False)

    timeout = models.DurationField(null=True, blank=True)
    task_type = models.CharField(max_length=2, choices=TaskTypeChoices.choices, default=DEFAULT_TYPE)

    def __str__(self):
        return str(self.name)


class TaskExecution(models.Model):
    class StatusChoices(models.TextChoices):
        RUNNING = "R", _("Running")
        SUCCESS = "S", _("Success")
        FAILED = "F", _("Failed")
        PENDING = "P", _("Pending")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING, db_index=True)
    celery_task_id = models.CharField(max_length=50, null=True, blank=True)
    log = models.FileField(upload_to=task_execution_log_file_directory_path, null=True, blank=True)
    run_time = models.IntegerField(blank=True, null=True)  # in seconds
    extracted_datasets = models.ManyToManyField(Dataset, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
