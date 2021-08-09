from django.forms import ModelForm
from workflows.models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['docker_image', 'name']
