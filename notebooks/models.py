from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Session(models.Model):
    class SessionStatus(models.TextChoices):
        NOTRUNNING = "NR", _("Not Running")
        RUNNING = "R", _("Running")
        ENDED = "E", _("Ended")

    uuid = models.CharField(max_length=255)
    container_id = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=3, choices=SessionStatus.choices, default=SessionStatus.NOTRUNNING)
    run_counter = models.IntegerField(default=1)

class Notebook(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

class Cell(models.Model):
    class CellStatus(models.TextChoices):
        PENDING = "P", _("Pending")
        RUNNING = "R", _("Running")
        DONE = "D", _("Done")

    code = models.TextField()
    result = models.TextField()
    cell_status = models.CharField(max_length=2, choices=CellStatus.choices, default=CellStatus.PENDING)
