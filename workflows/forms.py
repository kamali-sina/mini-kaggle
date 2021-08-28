from datetime import timedelta
from datetime import datetime
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError

from workflows.models import Secret, Task, PythonTask, Workflow, DockerTask, WorkflowSchedule


class TaskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['notification_source'].label = 'Select a notification source for this task'
        self.fields['notification_source'].queryset = self.creator.notification_sources
        self.fields['workflow'] = forms.ModelChoiceField(
            queryset=Workflow.objects.filter(creator=self.creator))
        self.fields['accessible_datasets'].label = 'Select the datasets this task will make use of'
        self.fields['accessible_datasets'].queryset = self.creator.datasets
        self.fields['timeout'].help_text = 'leave empty, for no time limit'
        self.fields['secret_variables'].label = 'Add secret variable to task execution'
        self.fields['secret_variables'].queryset = Secret.objects.filter(creator=self.creator)

    def clean(self):
        cleaned_data = super().clean()
        alert_on_failure = cleaned_data.get("alert_on_failure")
        notification_source = cleaned_data.get("notification_source")

        if alert_on_failure and not notification_source:
            raise ValidationError('No notification source selected!')

    class Meta:
        model = Task
        fields = ['name', 'timeout', 'secret_variables', 'accessible_datasets', 'notification_source',
                  'alert_on_failure', 'workflow']


class PythonTaskForm(TaskForm):
    class Meta:
        model = PythonTask
        fields = ['name', 'timeout', 'secret_variables', 'accessible_datasets', 'notification_source',
                  'alert_on_failure', 'python_file', 'docker_image', 'workflow']


class DockerTaskForm(TaskForm):
    class Meta:
        model = DockerTask
        fields = ["name", "docker_image", 'secret_variables', 'timeout', 'accessible_datasets', 'notification_source',
                  'alert_on_failure', 'workflow']


class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow
        fields = ['name']


class SecretForm(ModelForm):
    class Meta:
        model = Secret
        fields = ['name', "value"]


class WorkflowScheduleForm(ModelForm):
    class Meta:
        model = WorkflowSchedule
        fields = ['start_time', 'schedule_interval']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget.attrs['placeholder'] = datetime.now()
        self.fields['schedule_interval'].widget.attrs['placeholder'] = timedelta()
