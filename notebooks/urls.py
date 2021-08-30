from django.urls import path

from . import views

app_name = "notebooks"
urlpatterns = [
    # notebook crud
    path("", views.NotebooksListView.as_view(), name="index"),
    path("<int:pk>/", views.NotebookDetailView.as_view(), name="detail"),
    path("<int:pk>/delete", views.NotebookDeleteView.as_view(), name="delete"),
    # cell api
    path("cell/create/", views.cell_create_view, name="cell_create"),
    path("cell/update/<int:pk>/", views.cell_update_view, name="cell_create"),
    path("cell/delete/<int:pk>/", views.cell_delete_view, name="cell_create"),
]
