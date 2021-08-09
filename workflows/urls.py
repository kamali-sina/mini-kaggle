from django.urls import path
from . import views

app_name = 'workflows'
urlpatterns = [
    path('task/', views.TaskListView.as_view(), name='list_task'),
    path('task/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='detail_task'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
]
