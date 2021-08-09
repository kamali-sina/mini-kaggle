from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path("", views.DatasetIndexView.as_view(), name="index"),
    path("public", views.PublicView.as_view(), name="public"),
    path("<int:pk>/", views.DatasetDetailView.as_view(), name="detail"),
    path("upload/", views.dataset_add_dataset, name="upload"),
]
