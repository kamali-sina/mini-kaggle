from django.core.files.base import ContentFile
from django.forms import ModelForm
from django.shortcuts import reverse

from notebooks.models import Notebook
from notebooks.services.export import get_notebook_code
from workflows.models import Task, Secret

from workflows.models import PythonTask


class NotebookForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['accessible_datasets'].label = 'Select the datasets this task will make use of'
        self.fields['accessible_datasets'].queryset = self.creator.datasets

    class Meta:
        model = Notebook
        fields = ['name', 'accessible_datasets']

    def save(self, commit=True):
        notebook = super().save(commit=False)
        notebook.creator = self.creator
        if commit:
            notebook.save()
            self.save_m2m()
        return notebook


class ExportNotebookForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        self.notebook = kwargs.pop('notebook')
        super().__init__(*args, **kwargs)
        self.fields['notification_source'].label = 'Select a notification source for this task'
        self.fields['notification_source'].queryset = self.creator.notification_sources
        self.fields['accessible_datasets'].label = 'Select the datasets this task will make use of'
        self.fields['accessible_datasets'].queryset = self.creator.datasets
        self.fields['timeout'].help_text = 'leave empty, for no time limit'
        self.fields['secret_variables'].label = 'Add secret variable to task execution'
        self.fields['secret_variables'].queryset = Secret.objects.filter(creator=self.creator)
        self.fields['docker_image'].initial = "python:3.8-slim-buster"
        setattr(self.fields['notification_source'], 'create_link', reverse('notifications:create'))

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
