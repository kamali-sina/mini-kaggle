from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path("", views.DatasetIndexView.as_view(), name="index"),
    path("public", views.PublicView.as_view(), name="public"),
    path("<int:pk>/", views.dataset_detail_view, name="detail"),
    path("<int:pk>/download/", views.dataset_download_view, name="download"),
    path("upload/", views.dataset_add_dataset, name="upload"),
    path("<int:pk>/edit", views.edit_dataset_view, name="edit")
]
