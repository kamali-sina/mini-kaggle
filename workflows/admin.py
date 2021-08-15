from django.contrib import admin
from workflows.models import PythonTask, Task, Workflow

# Register your models here.

admin.site.register(Task)
admin.site.register(PythonTask)
admin.site.register(Workflow)
