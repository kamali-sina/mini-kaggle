from .task import TaskListView, TaskCreateView, TaskDeleteView, TaskDetailView
from .workflow import WorkflowListView, WorkflowCreateView, WorkflowDeleteView, WorkflowDetailView, \
    WorkflowScheduleRedirectView
from .secret import SecretListView, SecretCreateView, SecretDeleteView, SecretDetailView, SecretCreatorOnlyMixin
