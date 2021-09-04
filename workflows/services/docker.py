import signal
import sys
import os
from io import BytesIO
from enum import Enum
import tarfile
import shutil
import docker
from celery.result import AsyncResult

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from datasets.models import Dataset, is_file_valid, DATASETS_MEDIA_PATH
from workflows.models import Task, TaskExecution
from .task_data import get_task_data

CREATED_DATASETS_NAME_ABSTRACT = 'created_by_%s'
CPU_PERIOD = 100000
CPU_QUOTA = 50000 # The number of microseconds per cpu-period that the container is limited to before throttled
MEMORY_LIMIT = '20m'


def add_file_to_datasets(file_path, filename, task_execution):
    user = task_execution.task.creator
    task_name = task_execution.task.name
    dataset_title = CREATED_DATASETS_NAME_ABSTRACT % task_name
    path_in_media = DATASETS_MEDIA_PATH % str(user.username)
    os.makedirs(settings.MEDIA_ROOT + path_in_media, exist_ok=True)
    os.replace(file_path, settings.MEDIA_ROOT + path_in_media + filename)
    dataset = Dataset.objects.create(creator=user, file=path_in_media + filename, title=dataset_title)
    task_execution.extracted_datasets.add(dataset)
    task_execution.save()


def recieve_dataset_from_container(extract_path, docker_container):
    file_stream = BytesIO()
    try:
        bits, _ = docker_container.get_archive(DockerTaskService.container_extract_datasets_path)
    except docker.errors.NotFound:
        return False
    for chunk in bits:
        file_stream.write(chunk)
    file_stream.seek(0)
    with tarfile.open(fileobj=file_stream) as tar_file:
        tar_file.extractall(path=extract_path)
    file_stream.close()
    return True


def check_validity_of_datasets(extracted_files_dir):
    for file in os.listdir(extracted_files_dir):
        if not is_file_valid(file):
            return False
    return True


def exctract_dataset_from_execution(task_execution, docker_container):
    extract_path = f"./task_{task_execution.id}"
    if not recieve_dataset_from_container(extract_path, docker_container):
        # There is no data to be extracted
        return
    extracted_files_dir = extract_path + DockerTaskService.container_extract_datasets_path
    if not check_validity_of_datasets(extracted_files_dir):
        raise ValidationError(f"Not all files in the \
                            {DockerTaskService.container_extract_datasets_path} folder \
                            were valid! No datasets are saved.")
    for file in os.listdir(extracted_files_dir):
        file_path = os.path.abspath(extracted_files_dir + file)
        add_file_to_datasets(file_path, file, task_execution)
    shutil.rmtree(extract_path, ignore_errors=True)


def task_status_color(status):
    if status == "Failed":
        return "#c0392b"
    if status == "Success":
        return "#27ae60"
    return "#bdc3c7"


class MarkTaskExecutionStatusOptions(Enum):
    FAILED = 0
    SUCCESS = 1


def get_task_type(task):
    return get_task_data(task)["name"]


def get_special_display_fields(task):
    task_map = get_task_data(task)
    if task.__class__ == Task:
        task = getattr(task, task_map["task_related_name"])
    return {
        field_name.replace("_", " "): getattr(task, field_name)
        for field_name in task_map["display_fields"]
    }


def read_task_execution_log_file(task_execution):
    if task_execution.log:
        with open(task_execution.log.path, encoding="utf-8") as log_file:
            return log_file.read()
    else:
        raise FileNotFoundError("log not found")


def set_task_execution_log_file(task_execution, log):
    task_execution.log.save(task_execution.pk, ContentFile(log))
    task_execution.save()


class DockerTaskService:
    accessible_datasets_path = '/datasets/'
    container_extract_datasets_path = '/results/'

    @staticmethod
    def get_environment(task):
        return {secret.name: secret.value
                for secret in task.secret_variables.all()}

    @staticmethod
    def run_container(task_execution, **kwargs):
        """
        Creates a docker client using from_env
        Runs a new docker container in the background(detach=True) using containers.run
        Customize the docker image by editing the first field of client.containers.run
        Set memory limit using mem_limit.
        Set cpu usage limit for the container using cpu period and cpu quota.
        For more information on cpu quota visit:
            https://docs.docker.com/config/containers/resource_constraints/#configure-the-default-cfs-scheduler
        wait for finish work
        save log
        return container status
        """

        def stop_container_on_signal(sig, frame):
            # pylint: disable=unused-argument
            container.stop()

            task_execution.status = TaskExecution.StatusChoices.FAILED
            task_execution.save()

            sys.exit(0)

        client = docker.from_env()
        try:
            container = client.containers.run(**kwargs, detach=True, cpu_period=CPU_PERIOD, cpu_quota=CPU_QUOTA,
                                              mem_limit=MEMORY_LIMIT)
            signal.signal(signal.SIGTERM, stop_container_on_signal)
            container.wait()
            container = client.containers.get(container.id)
            exctract_dataset_from_execution(task_execution, container)
            container_log = container.logs().decode("utf-8")
            set_task_execution_log_file(task_execution, container_log)
            if container.attrs["State"]["ExitCode"] == 0:
                return TaskExecution.StatusChoices.SUCCESS
            return TaskExecution.StatusChoices.FAILED
        except docker.errors.ContainerError:
            container_log = container.logs().decode("utf-8")
            set_task_execution_log_file(task_execution, container_log)
            return TaskExecution.StatusChoices.FAILED
        except:  # pylint: disable=bare-except
            return TaskExecution.StatusChoices.FAILED

    def run_task(self, task_execution):
        task = task_execution.task
        run_container_kwargs = {"image": task.dockertask.docker_image,
                                "volumes": DockerTaskService.get_accessible_datasets_mount_dict(task),
                                "environment": self.get_environment(task)}
        return self.run_container(task_execution, **run_container_kwargs)

    @staticmethod
    def stop_task_execution(
            task_execution_id: str,
            mark_task_execution_status_as: MarkTaskExecutionStatusOptions,
    ):
        task_execution = TaskExecution.objects.get(id=task_execution_id)
        try:
            AsyncResult(task_execution.celery_task_id).revoke(terminate=True, signal="SIGTERM")
        except ValueError:
            pass  # task execution dont have valid task id
        if mark_task_execution_status_as == MarkTaskExecutionStatusOptions.FAILED:
            task_execution.status = TaskExecution.StatusChoices.FAILED
        elif mark_task_execution_status_as == MarkTaskExecutionStatusOptions.SUCCESS:
            task_execution.status = TaskExecution.StatusChoices.SUCCESS
        else:
            raise ValidationError("invalid mark status choice")
        task_execution.save()

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
