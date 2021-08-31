from django.urls import path

from . import views

app_name = "notebooks"
urlpatterns = [
    path("", views.NotebooksListView.as_view(), name="index"),
    path("<int:pk>/", views.NotebookDetailView.as_view(), name="detail"),
    path("<int:pk>/delete", views.NotebookDeleteView.as_view(), name="delete"),
    path("<int:pk>/export", views.ExportNotebook.as_view(), name="export"),
]
