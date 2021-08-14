from django.core.mail import send_mail
from django.conf import settings


def send_email_notification(message, receiver_mail):
    send_mail("subject",
              message,
              settings.EMAIL_HOST_USER,
              [receiver_mail],
              fail_silently=False)
