from django.contrib import admin
from workflows.models import PythonTask, Task

# Register your models here.

admin.site.register(Task)
admin.site.register(PythonTask)