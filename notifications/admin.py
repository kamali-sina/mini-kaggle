from django.contrib import admin

# Register your models here.

from notifications.models import EmailNotificationSource

admin.site.register(EmailNotificationSource)
