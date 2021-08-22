import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from notifications.models import EmailNotificationSource

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def email_list_validator(value):
    emails = re.split(r'\s+', value)
    for email in emails:
        if not re.match(EMAIL_REGEX, email):
            raise ValidationError(
                _('%(value)s is not a valid email address'),
                params={'value': email},
            )


class CreateEmailNotificationSourceForm(forms.ModelForm):
    recipients = forms.CharField(label='Add white-space separated emails',
                                 required=True,
                                 max_length=1000,
                                 validators=[email_list_validator],
                                 widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        model = EmailNotificationSource
        fields = ["title", "recipients"]

    def clean_recipients(self):
        return list(set(re.split(r'\s+', self.cleaned_data['recipients'])))

    def save(self, commit=True):
        notification = super().save(commit=False)
        notification.user = self.user
        if commit:
            notification.save()
        return notification
