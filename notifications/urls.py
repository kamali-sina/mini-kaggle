from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('create/', views.create_notification_source, name='create'),
    path('create/forms/<str:notification_type>/', views.get_typed_notification_form, name='typed_form')
]
