from django.db import models
from workflows.models import Task, Workflow


class TaskDependency(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    parent_tasks = models.ManyToManyField('self', blank=True)
