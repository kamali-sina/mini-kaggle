import os
from enum import Enum
import docker
from django.core.exceptions import ValidationError
from workflows.models import Task, TaskExecution, DockerTaskExecution
from .task_data import get_task_data


def task_status_color(status):
    if status == "Failed":
        return "#c0392b"
    if status == "Success":
        return "#27ae60"
    return "#bdc3c7"


class MarkTaskExecutionStatusOptions(Enum):
    FAILED = 0
    SUCCESS = 1


def get_display_fields(task):
    task_map = get_task_data(task)
    if task.__class__ == Task:
        task = getattr(task, task_map["task_related_name"])

    return {
        field_name.replace("_", " "): getattr(task, field_name)
        for field_name in task_map["display_fields"]
    }


def get_task_type(task):
    return get_task_data(task)["name"]


class DockerTaskService():
    accessible_datasets_path = '/datasets/'

    def run_task(self, task):
        """
        Creates a docker client using from_env
        Runs a new docker container in the background(detach=True) using containers.run
        Customize the docker image by editing the first field of client.containers.run
        """

        client = docker.from_env()
        container = client.containers.run(task.dockertask.docker_image,
                                          volumes=DockerTaskService.get_accessible_datasets_mount_dict(task),
                                          detach=True,
                                          environment=self.get_environment(task)
                                          )
        DockerTaskExecution.objects.create(task=task, container_id=container.id,
                                           status=TaskExecution.StatusChoices.RUNNING)

    @staticmethod
    def stop_task_execution(
            task_execution_id: str,
            mark_task_execution_status_as: MarkTaskExecutionStatusOptions,
    ):
        client = docker.from_env()
        docker_task_execution = DockerTaskExecution.objects.get(id=task_execution_id)
        container = client.containers.get(container_id=docker_task_execution.container_id)
        if mark_task_execution_status_as == MarkTaskExecutionStatusOptions.FAILED:
            docker_task_execution.status = TaskExecution.StatusChoices.FAILED
        elif mark_task_execution_status_as == MarkTaskExecutionStatusOptions.SUCCESS:
            docker_task_execution.status = TaskExecution.StatusChoices.SUCCESS
        else:
            raise ValidationError("invalid mark status choice")
        container.stop()
        docker_task_execution.save()

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

    # pylint: disable=no-member
    @staticmethod
    def _task_execution_status(task_execution):
        client = docker.from_env()
        container = client.containers.get(task_execution.dockertaskexecution.container_id)
        status = TaskExecution.StatusChoices.RUNNING
        if container.status in ["running", "restarting"]:
            status = TaskExecution.StatusChoices.RUNNING
        elif container.status == "exited":
            if container.attrs["State"]["ExitCode"] != 0:
                status = TaskExecution.StatusChoices.FAILED
            else:
                status = TaskExecution.StatusChoices.SUCCESS

            task_execution.status = status
            task_execution.save()

        return status.name

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

    @staticmethod
    def get_environment(task):
        return {secret.name: secret.value
                for secret in task.secret_variables.all()}

    @staticmethod
    def get_accessible_datasets_mount_info(task):
        info = []
        for dataset in task.accessible_datasets.all():
            info.append(DockerTaskService._get_dataset_mount_path(dataset))
        return info

    @staticmethod
    def _get_dataset_mount_path(dataset):
        return f'{DockerTaskService.accessible_datasets_path}{dataset.title}{os.path.splitext(dataset.file.name)[1]}'

    @staticmethod
    def get_accessible_datasets_mount_dict(task):
        volumes = {}
        for dataset in task.accessible_datasets.all():
            volumes.update({dataset.file.path: {
                'bind': f'{DockerTaskService.accessible_datasets_path}{dataset.title}{os.path.splitext(dataset.file.name)[1]}',
                'mode': 'ro'}})
        return volumes
