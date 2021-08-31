from django.contrib import admin
from workflows.models import PythonTask, Task, Workflow, WorkflowExecution, WorkflowSchedule, TaskExecution
from workflows.models.task_dependency import TaskDependency, TaskDependencyExecution

# Register your models here.

admin.site.register(Task)
admin.site.register(PythonTask)
admin.site.register(Workflow)
admin.site.register(WorkflowExecution)
admin.site.register(WorkflowSchedule)
admin.site.register(TaskDependency)
admin.site.register(TaskDependencyExecution)
admin.site.register(TaskExecution)
