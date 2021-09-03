from workflows.models import DockerTask, PythonTask, Task, TaskExecution

tasks_data = {
    DockerTask:
        {
            "name": "Docker",
            "task_related_name": "dockertask",
            "display_fields": ["docker_image"],
        },

    PythonTask:
        {
            "name": "Python",
            "task_related_name": "pythontask",
            "display_fields": ["python_file", "docker_image"],
        }
}


def get_task_data(task):
    # convert task execution to task
    if isinstance(task, TaskExecution):
        task = task.task

    # convert inheritance object to task
    if task.__class__ != Task:
        task = task.task_ptr

    for data in tasks_data.values():
        if hasattr(task, data["task_related_name"]):
            return data

    raise Exception("Service not found!")
