from django.conf import settings
from django.contrib.auth.models import User

from django.views.generic import CreateView

# Create your views here.
from .forms import UserForm


class Signup(CreateView):
    model = User
    form_class = UserForm
    template_name = 'registration/signup.html'
    success_url = settings.LOGIN_URL
