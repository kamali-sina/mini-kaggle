from django.forms import ModelForm
from workflows.models import Task, PythonTask, Workflow
from django import forms
from django.core.exceptions import ValidationError


class TaskForm(ModelForm):
    accessible_datasets = forms.ModelMultipleChoiceField(queryset=None,
                                                         required=False,
                                                         label='Select the datasets this task will make use of')
    notification_source = forms.ModelChoiceField(queryset=None,
                                                 required=False,
                                                 label='Select a notification source for this task')

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['notification_source'].queryset = self.creator.notification_sources
        self.fields['workflow'] = forms.ModelChoiceField(
            queryset=Workflow.objects.filter(creator=self.creator))
        self.fields['accessible_datasets'].queryset = self.creator.datasets
        self.fields['timeout'].help_text = 'leave empty, for no time limit'

    def clean(self):
        cleaned_data = super().clean()
        alert_on_failure = cleaned_data.get("alert_on_failure")
        notification_source = cleaned_data.get("notification_source")

        if alert_on_failure and not notification_source:
            raise ValidationError('No notification source selected!')

    class Meta:
        model = Task
        fields = ['name', 'timeout', 'accessible_datasets', 'notification_source', 'alert_on_failure', 'workflow']


class PythonTaskForm(TaskForm):
    class Meta:
        model = PythonTask
        fields = ['name', 'timeout', 'accessible_datasets', 'notification_source', 'alert_on_failure', 'python_file',
          'docker_image']


class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow
        fields = ['name']
