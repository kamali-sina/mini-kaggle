from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notebook/(?P<notebook_id>\d+)/$', consumers.NotebookConsumer.as_asgi()),
]
