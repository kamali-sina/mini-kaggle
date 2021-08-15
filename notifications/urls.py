from django.urls import path
from . import views

app_name = 'notifications'
urlpatterns = [
    path('create/email', views.CreateEmailNotificationSource.as_view(), name='create_email_notif')
]
