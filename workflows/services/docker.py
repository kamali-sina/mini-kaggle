import os
from enum import Enum
import docker

from django.core.exceptions import ValidationError
from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.task import TaskService


class MarkTaskExecutionStatusOptions(Enum):
    FAILED = 0
    SUCCESS = 1


class DockerTaskService(TaskService):
    accessible_datasets_path = '/datasets/'

    @staticmethod
    def get_environment(task):
        return {secret.name: secret.value
                for secret in task.secret_variables.all()}

    def run_task(self, task):
        client = docker.from_env()
        container = client.containers.run(task.dockertask.docker_image,
                                          volumes=DockerTaskService.get_accessible_datasets_mount_dict(task),
                                          detach=True,
                                          environment=self.get_environment(task)
                                          )
        DockerTaskExecution.objects.create(task=task, container_id=container.id,
                                           status=TaskExecution.StatusChoices.RUNNING)

    def stop_task_execution(
            self,
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

    # pylint: disable=no-member
    def _task_execution_status(self, task_execution):
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
