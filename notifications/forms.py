import json
import re
from django import forms
from notifications.models import EmailNotificationSource
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def email_list_validator(value):
    emails = re.split(r'\s+', value)
    for email in emails:
        if not re.match(email_regex, email):
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
        super(CreateEmailNotificationSourceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = EmailNotificationSource
        fields = ["recipients"]

    def clean_recipients(self):
        return list(set(re.split(r'\s+', self.cleaned_data['recipients'])))

    def save(self, commit=True):
        notification = super(CreateEmailNotificationSourceForm, self).save(commit=False)
        notification.user = self.user
        if commit:
            notification.save()
        return notification
