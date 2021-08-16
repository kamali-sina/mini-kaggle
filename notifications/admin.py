from django.contrib import admin

# Register your models here.

from notifications.models import NotificationSource, EmailNotificationSource

admin.site.register(NotificationSource)
admin.site.register(EmailNotificationSource)
