from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib import messages
from .forms import UserForm


class Signup(CreateView):
    model = User
    form_class = UserForm
    template_name = 'registration/signup.html'
    success_url = settings.LOGIN_URL

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'You successfully registered :)')
        return HttpResponseRedirect(self.success_url)


def dashboard(request):
    return render(request, "dashboard.html")
