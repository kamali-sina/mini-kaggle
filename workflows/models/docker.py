from django.db import models
from workflows.models.task import Task, TaskExecution

class DockerTask(Task):
    docker_image = models.CharField(max_length=255)

class DockerTaskExecution(TaskExecution):
    container_id = models.CharField(max_length=255)
