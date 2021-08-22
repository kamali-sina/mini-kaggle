from workflows.services.docker import DockerTaskService
from workflows.services.python import PythonTaskService
from .task_data import get_task_data


def get_service_runner(task):
    task_map = get_task_data(task)
    task_type = task_map["name"]

    if task_type == "Docker":
        return DockerTaskService()
    if task_type == "Python":
        return PythonTaskService()
    raise Exception("Invalid task type!")
