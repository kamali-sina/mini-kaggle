from abc import ABC, abstractmethod
from workflows.models import Task, TaskExecution
from .task_data import get_task_data


def task_status_color(status):
    if status == "Failed":
        return "#c0392b"
    if status == "Success":
        return "#27ae60"
    return "#bdc3c7"


# pylint: disable=no-self-use
class TaskService(ABC):
    @abstractmethod
    def run_task(self, task):
        pass

    def get_display_fields(self, task):
        task_map = get_task_data(task)
        if task.__class__ == Task:
            task = getattr(task, task_map["task_related_name"])

        return {
            field_name.replace("_", " "): getattr(task, field_name)
            for field_name in task_map["display_fields"]
        }

    def get_task_type(self, task):
        return get_task_data(task)["name"]

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
        return task_execution.get_status_display()
