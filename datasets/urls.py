from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("public", views.PublicView.as_view(), name="public"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("upload/", views.uploadData, name="upload"),
]
