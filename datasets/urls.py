from django.urls import path

from . import views

app_name = "datasets"
urlpatterns = [
    path("", views.DatasetIndexView.as_view(), name="index"),
    path("<int:pk>/", views.dataset_detail_view, name="detail"),
    path("upload/", views.dataset_add_dataset, name="upload"),
]
