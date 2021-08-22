import os
import docker
from io import BytesIO
import tarfile
import shutil

from requests.sessions import extract_cookies_to_jar

from datasets.models import Dataset, is_file_valid
from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.task import TaskService
from django.conf import settings


class DockerTaskService(TaskService):
    accessible_datasets_path = '/datasets/'
    container_extract_datasets_path = '/results/'

    def run_task(self, task):
        client = docker.from_env()
        container = client.containers.run(task.dockertask.docker_image,
                                          volumes=DockerTaskService.get_accessible_datasets_mount_dict(task),
                                          detach=True)
        DockerTaskExecution.objects.create(task=task, container_id=container.id,
                                           status=TaskExecution.StatusChoices.RUNNING)

    @staticmethod
    def get_accessible_datasets_mount_dict(task):
        volumes = {}
        for dataset in task.accessible_datasets.all():
            volumes.update({dataset.file.path: {
                'bind': f'{DockerTaskService.accessible_datasets_path}{dataset.title}{os.path.splitext(dataset.file.name)[1]}',
                'mode': 'ro'}})
        return volumes

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
                self._exctract_data_from_execution(task_execution)

            task_execution.status = status
            task_execution.save()

        return status.name

    def _add_file_to_datasets(self, file_path, filename, task_execution):
        user = task_execution.task.creator
        task_name = task_execution.task.name
        path_in_media = "datasets/" + user.username + "/"
        os.makedirs(settings.MEDIA_ROOT + path_in_media, exist_ok=True)
        os.replace(file_path, settings.MEDIA_ROOT + path_in_media + filename)
        Dataset.objects.create(creator=user, file=path_in_media + filename, title=f"created_by_{task_name}")

    def _exctract_data_from_execution(self, task_execution):
        client = docker.from_env()
        container = client.containers.get(task_execution.dockertaskexecution.container_id)
        f = BytesIO()
        try:
            bits, stat = container.get_archive(self.container_extract_datasets_path)
        except:
            # There is no data to be extracted
            return
        for chunk in bits:
            f.write(chunk)
        f.seek(0)
        tar = tarfile.open(fileobj=f)
        task_execution_id = str(task_execution.id)
        extract_path = f"./task_{task_execution_id}"
        tar.extractall(path=extract_path)
        tar.close()
        f.close()
        extracted_files_dir = extract_path + self.container_extract_datasets_path
        for file in os.listdir(extracted_files_dir):
            if (not is_file_valid(file)):
                print(f'{file} is not a supported type')
            file_path = os.path.abspath(extracted_files_dir + file)
            self._add_file_to_datasets(file_path, file, task_execution)
        shutil.rmtree(extract_path, ignore_errors=True)