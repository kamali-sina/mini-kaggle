from django.db import models
from django.contrib.auth.models import User



class Secret(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)
