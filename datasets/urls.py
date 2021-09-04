from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path("", views.DatasetListView.as_view(visibility='private'), name="index"),
    path("public", views.DatasetListView.as_view(visibility='public'), name="public"),
    path("<int:pk>/", views.dataset_detail_view, name="detail"),
    path("<int:pk>/download/", views.dataset_download_view, name="download"),
    path("upload/", views.DatasetCreateView.as_view(), name="upload"),
    path("<int:pk>/edit", views.DatasetUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete", views.DatasetDeleteView.as_view(), name="delete"),
]
