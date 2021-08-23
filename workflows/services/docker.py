import os
import docker

from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.task import TaskService


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

    @staticmethod
    def get_accessible_datasets_mount_dict(task):
        volumes = {}
        for dataset in task.accessible_datasets.all():
            volumes.update({dataset.file.path: {
                'bind': DockerTaskService._get_dataset_mount_path(dataset),
                'mode': 'ro'}})
        return volumes

    @staticmethod
    def get_accessible_datasets_mount_info(task):
        info = []
        for dataset in task.accessible_datasets.all():
            info.append(DockerTaskService._get_dataset_mount_path(dataset))
        return info

    @staticmethod
    def _get_dataset_mount_path(dataset):
        return f'{DockerTaskService.accessible_datasets_path}{dataset.title}{os.path.splitext(dataset.file.name)[1]}'

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
