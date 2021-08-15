from abc import ABC, abstractmethod
from workflows.models import Task, DockerTask, PythonTask, TaskExecution


class TaskService(ABC):
    @abstractmethod
    def run_task(self, task):
        pass

    def task_status(self, task):

        # convert inherited object to task  if need
        if task.__class__ != Task:
            if issubclass(task.__class__, Task):
                task = task.task_ptr
            else:
                raise Exception("Wrong type object")

        task_executions = TaskExecution.objects.filter(task=task)
        if task_executions.count() == 0:
            return "None"
        else:
            return self.task_execution_status(task_executions.last())

    @abstractmethod
    def _task_execution_status(self, task_execution):
        pass

    def task_execution_status(self, task_execution):
        # convert inherited object to task execution if need
        if task_execution.__class__ != TaskExecution:
            if issubclass(task_execution.__class__, TaskExecution):
                task_execution = task_execution.taskexecution_ptr
            else:
                raise Exception("Wrong type object")

        if task_execution.status == task_execution.StatusChoices.RUNNING:
            return self._task_execution_status(task_execution)
        else:
            return task_execution.status
