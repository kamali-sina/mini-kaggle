from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from datasets.models import Dataset

CODE_SNIPPETS_DIR = './notebooks/static/notebooks/snippets'


class Session(models.Model):
    class SessionStatus(models.TextChoices):
        NOTRUNNING = "NR", _("Not Running")
        RUNNING = "R", _("Running")
        ENDED = "E", _("Ended")

    uuid = models.CharField(max_length=255)
    container_id = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=3, choices=SessionStatus.choices, default=SessionStatus.NOTRUNNING)
    run_counter = models.IntegerField(default=1)

    def __str__(self):
        return str(self.uuid)

class Notebook(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE, null=True, related_name="notebook")
    accessible_datasets = models.ManyToManyField(Dataset, blank=True)

    def __str__(self):
        return str(self.name)

class Cell(models.Model):
    class CellStatus(models.TextChoices):
        RUNNING = "R", _("Running")
        DONE = "D", _("Done")
        NONE = "N", _("None")

    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='cells', blank=True)
    code = models.TextField(null=True, blank=True)
    cell_status = models.CharField(max_length=1, choices=CellStatus.choices, default=CellStatus.NONE)
