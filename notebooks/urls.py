from django.urls import path

from . import views

app_name = "notebooks"
urlpatterns = [
    path("", views.NotebooksListView.as_view(), name="index"),
    path("create/", views.NotebookCreateView.as_view(), name="create"),
    path("<int:pk>/", views.NotebookDetailView.as_view(), name="detail"),
    path("<int:pk>/delete", views.NotebookDeleteView.as_view(), name="delete"),
    path("snippets", views.snippets_list_view, name="snippets"),
    path("snippets/<str:name>", views.snippet_detail_view, name="snippet_detail"),
    path("<int:pk>/export", views.ExportNotebook.as_view(), name="export"),
]
