from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class NotificationSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class EmailNotificationSource(NotificationSource):
    recipients = models.JSONField()
