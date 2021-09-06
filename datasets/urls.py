from django.urls import path

from . import views

app_name = "datasets"

datasets_urls = [
    path("", views.DatasetListView.as_view(visibility='private'), name="index"),
    path("public", views.DatasetListView.as_view(visibility='public'), name="public"),
    path("<int:pk>/", views.dataset_detail_view, name="detail"),
    path("<int:pk>/download/", views.dataset_download_view, name="download"),
    path("upload/", views.DatasetCreateView.as_view(), name="upload"),
    path("<int:pk>/edit/", views.DatasetUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.DatasetDeleteView.as_view(), name="delete"),
]

datasource_urls = [
    path("datasources/", views.DataSourceListView.as_view(), name="list_datasource"),
    path("datasources/create", views.DataSourceCreateView.as_view(), name="create_datasource"),
    path("datasources/<int:pk>/", views.datasource_detail_view, name="detail_datasource"),
    path("datasources/<int:pk>/delete", views.DataSourceDeleteView.as_view(), name="delete_datasource"),
]

urlpatterns = [
    *datasets_urls,
    *datasource_urls,
]
