from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('users/signup', views.Signup.as_view(), name='signup'),
    path('', views.dashboard, name='dashboard'),
]
