from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.


class NotificationSource(models.Model):
    class NotificationSourceType(models.TextChoices):
        EMAIL = 'EM', _("Email")

    DEFAULT_TYPE = NotificationSourceType.EMAIL

    title = models.CharField(max_length=200, default='Untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sources')
    type = models.CharField(max_length=5, choices=NotificationSourceType.choices, default=DEFAULT_TYPE)

    def cast(self):
        return getattr(self, NOTIFICATION_CHILD_REGISTRY[self.type])

    def __str__(self):
        return str(self.title)


class EmailNotificationSource(NotificationSource):
    recipients = models.JSONField()


NOTIFICATION_CHILD_REGISTRY = {
    NotificationSource.NotificationSourceType.EMAIL: 'emailnotificationsource'
}
