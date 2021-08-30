from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Notebook(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)

class Cell(models.Model):
    class CellStatus(models.TextChoices):
        PENDING = "P", _("Pending")
        RUNNING = "R", _("Running")
        DONE = "D", _("Done")
        NONE = "N", _("None")

    code = models.TextField()
    result = models.TextField(null=True,blank=True)
    cell_status = models.CharField(max_length=2, choices=CellStatus.choices, default=CellStatus.NONE)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)
