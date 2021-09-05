from django.core.files.base import ContentFile
from django.forms import ModelForm

from notebooks.models import Notebook
from notebooks.services.export import get_notebook_code
from workflows.models import Task

from workflows.models import PythonTask
from workflows.forms import TaskForm


class NotebookForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Notebook
        fields = ['name']

    def save(self, commit=True):
        notebook = super().save(commit=False)
        notebook.creator = self.creator
        if commit:
            notebook.save()
        return notebook


class ExportNotebookForm(TaskForm):
    def __init__(self, *args, **kwargs):
        self.notebook = kwargs.pop('notebook')

        super().__init__(*args, **kwargs)
        self.fields['docker_image'].initial = "python:3.8-slim-buster"

    class Meta:
        model = PythonTask
        fields = ['name', 'timeout', 'secret_variables', 'accessible_datasets', 'notification_source',
                  'alert_on_failure', 'docker_image']

    def save(self, commit=True):
        task = super().save(commit=False)
        task.creator = self.creator
        task.task_type = Task.TaskTypeChoices.PYTHON
        if commit:
            task.python_file.save(f"exported_{self.notebook.id}", ContentFile(get_notebook_code(self.notebook)))
            task.save()
            self.save_m2m()
        return task
