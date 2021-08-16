from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class NotificationSource(models.Model):
    title = models.CharField(max_length=200, default='Untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class EmailNotificationSource(NotificationSource):
    recipients = models.JSONField()
