from django.db import models
from workflows.models.task import Task


class DockerTask(Task):
    docker_image = models.CharField(max_length=255)
