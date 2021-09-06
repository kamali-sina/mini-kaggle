from datetime import timedelta
from datetime import datetime
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import reverse

from workflows.models import Secret, Task, PythonTask, Workflow, DockerTask, WorkflowSchedule
from workflows.models.task_dependency import TaskDependency


class TaskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        task_type = args[0]['task_type'] if args else Task.DEFAULT_TYPE
        self.typed_form = TASK_TYPED_FORM_REGISTRY[task_type](*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.fields['notification_source'].label = 'Select a notification source for this task'
        self.fields['notification_source'].queryset = self.creator.notification_sources
        self.fields['accessible_datasets'].label = 'Select the datasets this task will make use of'
        self.fields['accessible_datasets'].queryset = self.creator.datasets
        self.fields['timeout'].help_text = 'leave empty, for no time limit'
        self.fields['secret_variables'].label = 'Add secret variable to task execution'
        self.fields['secret_variables'].queryset = Secret.objects.filter(creator=self.creator)
        setattr(self.fields['notification_source'], 'create_link', reverse('notifications:create'))

    def is_valid(self):
        return super().is_valid() and self.typed_form.is_valid()

    def clean(self):
        cleaned_data = super().clean()
        alert_on_failure = cleaned_data.get("alert_on_failure")
        notification_source = cleaned_data.get("notification_source")

        if alert_on_failure and not notification_source:
            raise ValidationError('No notification source selected!')

    class Meta:
        model = Task
        non_m2m_fields = ['name', 'task_type', 'timeout', 'notification_source', 'alert_on_failure']
        m2m_fields = ['secret_variables', 'accessible_datasets']
        fields = non_m2m_fields + m2m_fields

    def save(self, commit=True):
        task = self.typed_form.save(commit=False)
        task.creator = self.creator
        for field in self.Meta.non_m2m_fields:
            setattr(task, field, self.cleaned_data[field])
        if commit:
            task.save()
            self.save_task_m2m(task)
        return task

    def save_task_m2m(self, task):
        for field in self.Meta.m2m_fields:
            getattr(task, field).set(self.cleaned_data[field])


class PythonTaskForm(forms.ModelForm):
    class Meta:
        model = PythonTask
        fields = ['python_file', 'docker_image']


class DockerTaskForm(forms.ModelForm):
    class Meta:
        model = DockerTask
        fields = ["docker_image"]


TASK_TYPED_FORM_REGISTRY = {
    Task.TaskTypeChoices.DOCKER: DockerTaskForm,
    Task.TaskTypeChoices.PYTHON: PythonTaskForm
}


class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'max_active_executions_count']


class TaskDependencyForm(forms.ModelForm):
    class Meta:
        fields = ['task', 'parent_tasks']
        model = TaskDependency

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        self.workflow_id = kwargs.pop('workflow_id')
        super().__init__(*args, **kwargs)
        self.fields['parent_tasks'].queryset = TaskDependency.objects.filter(workflow_id=self.workflow_id)
        used_tasks_id = self.fields['parent_tasks'].queryset.values_list('task', flat=True)
        self.fields['task'].queryset = Task.objects.filter(creator=self.creator).exclude(pk__in=used_tasks_id)


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
