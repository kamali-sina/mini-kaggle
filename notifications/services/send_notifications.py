from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from notifications.models import NotificationSource


def send_notification(notification, subject, template_name, context):
    template_string = render_to_string(template_name, context)
    notification_senders[notification.type](notification.cast(), subject, template_string)


def send_email_notification(notification, subject, body):
    send_mail(subject,
              body,
              settings.EMAIL_HOST_USER,
              notification.recipients,
              fail_silently=False)


notification_senders = {
    NotificationSource.NotificationSourceType.EMAIL: send_email_notification,
}
