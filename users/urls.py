from . import views
from django.contrib.auth import views as auth_views

from django.urls import path, include

app_name = 'users'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', views.Signup.as_view(), name='signup'),
]
