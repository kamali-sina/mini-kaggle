from django.db import models
from django.contrib import auth


class Workflow(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)
