from django.urls import path
from . import views

app_name = 'workflows'

workflows_urls = [
    path('', views.WorkflowListView.as_view(), name='list_workflow'),
    path('create/', views.WorkflowCreateView.as_view(), name='create_workflow'),
    path('<int:pk>/', views.WorkflowDetailView.as_view(), name='detail_workflow'),
    path('<int:pk>/dependencies/', views.TaskDependencyCreateView.as_view(), name='manage_dependencies'),
    path('<int:pk>/delete/', views.WorkflowDeleteView.as_view(), name='delete_workflow'),
    path('<int:pk>/run/', views.WorkflowRunView.as_view(), name='run_workflow'),
    path('<int:pk>/schedule/', views.WorkflowScheduleRedirectView.as_view(), name='schedule_workflow'),
    path('<int:pk>/schedule/paused/', views.workflow_schedule_paused_view, name='schedule_paused'),
]

tasks_urls = [
    path('tasks/', views.TaskListView.as_view(), name='list_task'),
    path('tasks/create/', views.create_task_view, name='create_task'),
    path('tasks/create/forms/<str:task_type>', views.get_typed_task_form, name='typed_form'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='detail_task'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('tasks/<int:pk>/executions/<int:exec_pk>/mark/', views.task.stop_task_execution_view,
         name='stop_task_execution'),
    path('tasks/<int:pk>/run/', views.task.run_task_view, name='run'),
]

secret_urls = [
    path('secrets/', views.SecretListView.as_view(), name='list_secret'),
    path('secrets/create/', views.SecretCreateView.as_view(), name='create_secret'),
    path('secrets/<int:pk>/', views.SecretDetailView.as_view(), name='detail_secret'),
    path('secrets/<int:pk>/delete/', views.SecretDeleteView.as_view(), name='delete_secret'),
]

urlpatterns = [
    path('tasks/executions/<int:pk>/', views.task.TaskExecutionDetailView.as_view(), name='detail_task_execution'),
    *tasks_urls,
    *secret_urls,
    *workflows_urls,
]
