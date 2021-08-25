from django.contrib import admin
from workflows.models import PythonTask, Task, Workflow, WorkflowSchedule
from workflows.models.task_dependency import TaskDependency

# Register your models here.

admin.site.register(Task)
admin.site.register(PythonTask)
admin.site.register(Workflow)
admin.site.register(WorkflowSchedule)
admin.site.register(TaskDependency)
