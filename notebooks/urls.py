from django.urls import path
from django.urls import re_path

from . import consumers
from . import views

app_name = "notebooks"

urlpatterns = [
    # notebook crud
    path("", views.NotebooksListView.as_view(), name="index"),
    path("create/", views.NotebookCreateView.as_view(), name="create"),
    path("<int:pk>/", views.NotebookDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.NotebookDeleteView.as_view(), name="delete"),
    path("<int:pk>/export/", views.ExportNotebook.as_view(), name="export"),
    path("<int:pk>/restart_kernel/", views.restart_kernel_view, name="restart_kernel"),
    # cell api
    path("<int:notebook_pk>/cell/create/", views.cell_create_view, name="cell_create"),
    path("<int:notebook_pk>/cell/update/<int:cell_pk>/", views.cell_update_view, name="cell_update"),
    path("<int:notebook_pk>/cell/delete/<int:cell_pk>/", views.cell_delete_view, name="cell_delete"),
    # code snippets
    path("snippets/", views.snippets_list_view, name="snippets"),
    path("snippets/<str:name>/", views.snippet_detail_view, name="snippet_detail"),
]

websocket_urlpatterns = [
    re_path(r'ws/notebook/(?P<notebook_id>\d+)/$', consumers.NotebookConsumer.as_asgi()),
]
