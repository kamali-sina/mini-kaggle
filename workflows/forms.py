from django.core import validators
from django.forms import ModelForm, FileField, FileInput
from workflows.models import Task, PythonTask


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['name']


class PythonTaskForm(ModelForm):
    class Meta:
        model = PythonTask
        fields = ["name", "python_file"]
