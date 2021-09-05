from django.db import models
from workflows.models import Task, TaskExecution, Workflow, WorkflowExecution


class TaskDependency(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='task_dependencies')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_index=True)
    parent_tasks = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return str(self.task.name)


class TaskDependencyExecution(models.Model):
    workflow_execution = models.ForeignKey(WorkflowExecution, on_delete=models.CASCADE,
                                           related_name='task_dependency_executions')
    task_execution = models.OneToOneField(TaskExecution, on_delete=models.PROTECT)
