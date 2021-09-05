import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from notifications.models import NotificationSource, EmailNotificationSource


class CreateNotificationSourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        notification_source_type = args[0]['type'] if args else NotificationSource.DEFAULT_TYPE
        self.typed_form = NOTIFICATION_TYPED_FORM_REGISTRY[notification_source_type](*args, **kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = NotificationSource
        fields = ["title", "type"]

    def is_valid(self):
        return super().is_valid() and self.typed_form.is_valid()

    def save(self, commit=True):
        notification_source = self.typed_form.save(commit=False)
        notification_source.user = self.user
        for field in self.Meta.fields:
            setattr(notification_source, field, self.cleaned_data[field])
        if commit:
            notification_source.save()
        return notification_source


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
    recipients = forms.CharField(label="Add recipients' emails",
                                 required=True,
                                 max_length=1000,
                                 validators=[email_list_validator],
                                 widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.fields['recipients'], 'interactive_input', True)

    class Meta:
        model = EmailNotificationSource
        fields = ["recipients"]

    def clean_recipients(self):
        return list(set(re.split(r'\s+', self.cleaned_data['recipients'])))


NOTIFICATION_TYPED_FORM_REGISTRY = {
    NotificationSource.NotificationSourceType.EMAIL: CreateEmailNotificationSourceForm
}
