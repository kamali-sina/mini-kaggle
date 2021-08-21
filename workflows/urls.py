from django.urls import path
from . import views

app_name = 'workflows'

workflows_urls = [
    path('', views.WorkflowListView.as_view(), name='list_workflow'),
    path('create/', views.WorkflowCreateView.as_view(), name='create_workflow'),
    path('<int:pk>/', views.WorkflowDetailView.as_view(), name='detail_workflow'),
    path('<int:pk>/delete/', views.WorkflowDeleteView.as_view(), name='delete_workflow'),
]

tasks_urls = [
    path('tasks/', views.TaskListView.as_view(), name='list_task'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='detail_task'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
]

urlpatterns = [
    *tasks_urls,
    *workflows_urls,
]
