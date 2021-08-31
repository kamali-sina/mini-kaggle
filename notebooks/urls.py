from django.urls import path

from . import views

app_name = "notebooks"
urlpatterns = [
    path("", views.NotebooksListView.as_view(), name="index"),
    path("<int:pk>/", views.NotebookDetailView.as_view(), name="detail"),
    path("<int:pk>/delete", views.NotebookDeleteView.as_view(), name="delete"),
    path("snippets", views.snippets_list_view, name="snippets"),
    path("snippets/<str:name>", views.snippet_detail_view, name="snippet_detail"),
]
