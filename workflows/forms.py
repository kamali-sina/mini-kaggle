from django.forms import ModelForm
from workflows.models import Task, PythonTask
from django import forms
from django.core.exceptions import ValidationError


class TaskForm(ModelForm):
    notification_source = forms.ModelChoiceField(queryset=None,
                                                 required=False,
                                                 label='Select a notification source for this task')

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['notification_source'].queryset = self.creator.notification_sources

    def clean(self):
        cleaned_data = super().clean()
        alert_on_failure = cleaned_data.get("alert_on_failure")
        notification_source = cleaned_data.get("notification_source")

        if alert_on_failure and not notification_source:
            raise ValidationError('No notification source selected!')

    class Meta:
        model = Task
        fields = ['name', 'notification_source', 'alert_on_failure']


class PythonTaskForm(ModelForm):
    class Meta:
        model = PythonTask
        fields = ["name", "python_file"]
