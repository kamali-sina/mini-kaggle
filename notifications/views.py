from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from notifications.models import EmailNotificationSource
from notifications.forms import CreateEmailNotificationSourceForm
from django.urls import reverse


# Create your views here.

class CreateEmailNotificationSource(LoginRequiredMixin, generic.CreateView):
    model = EmailNotificationSource
    form_class = CreateEmailNotificationSourceForm
    template_name = 'notifications/create_email_notification.html'

    def get_form_kwargs(self):
        kwargs = super(CreateEmailNotificationSource, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('dashboard')
