from django.db import models
from django.contrib.auth.models import User


class Workflow(models.Model):
    name = models.CharField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
