from django.urls import path
from . import views

app_name = 'workflows'

workflows_urls = [
    path('workflows/<int:pk>/', views.WorkflowDetailView.as_view(), name='detail_workflow'),
    path('workflows/<int:pk>/delete/', views.WorkflowDeleteView.as_view(), name='delete_workflow'),
]

tasks_urls = [
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='detail_task'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('tasks/create/python', views.PythonTaskCreateView.as_view(), name='create_python_task'),
]

urlpatterns = [
    path('tasks/', views.TaskListView.as_view(), name='list_task'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('workflows/', views.WorkflowListView.as_view(), name='list_workflow'),
    path('workflows/create/', views.WorkflowCreateView.as_view(), name='create_workflow'),
    *tasks_urls,
    *workflows_urls,
]