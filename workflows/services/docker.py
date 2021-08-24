import os
from io import BytesIO
import tarfile
import shutil
import docker
from docker.errors import APIError

from django.conf import settings
from datasets.models import Dataset, is_file_valid
from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.task import TaskService

def add_file_to_datasets(file_path, filename, task_execution):
    user = task_execution.task.creator
    task_name = task_execution.task.name
    path_in_media = "datasets/" + user.username + "/"
    os.makedirs(settings.MEDIA_ROOT + path_in_media, exist_ok=True)
    os.replace(file_path, settings.MEDIA_ROOT + path_in_media + filename)
    Dataset.objects.create(creator=user, file=path_in_media + filename, title=f"created_by_{task_name}")

class DockerTaskService(TaskService):
    accessible_datasets_path = '/datasets/'
    container_extract_datasets_path = '/results/'

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
                self.exctract_data_from_execution(task_execution)

            task_execution.status = status
            task_execution.save()

        return status.name

    def _recieve_data_from_container(self, task_execution, extract_path):
        client = docker.from_env()
        container = client.containers.get(task_execution.dockertaskexecution.container_id)
        file_stream = BytesIO()
        try:
            bits, _ = container.get_archive(self.container_extract_datasets_path)
        except APIError:
            return False
        for chunk in bits:
            file_stream.write(chunk)
        file_stream.seek(0)
        with tarfile.open(fileobj=file_stream) as tar_file:
            tar_file.extractall(path=extract_path)
        file_stream.close()
        return True

    def exctract_data_from_execution(self, task_execution):
        extract_path = f"./task_{task_execution.id}"
        if not self._recieve_data_from_container(task_execution, extract_path):
            # There is no data to be extracted
            return
        extracted_files_dir = extract_path + self.container_extract_datasets_path
        for file in os.listdir(extracted_files_dir):
            if not is_file_valid(file):
                print(f'{file} is not a supported type')
            file_path = os.path.abspath(extracted_files_dir + file)
            add_file_to_datasets(file_path, file, task_execution)
        shutil.rmtree(extract_path, ignore_errors=True)
