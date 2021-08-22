from django.core import validators
from django.db import models
from .task import Task


def user_python_file_directory_path(instance, filename):
    # file will be uploaded to MEDIAROOT/user<id>/datasets/<filename>
    return f"workflows/python_files/{instance.creator.username}/{filename}"


class PythonTask(Task):
    python_file = models.FileField(
        upload_to=user_python_file_directory_path,
        validators=[
            validators.FileExtensionValidator(allowed_extensions=["py"]),
        ])

    docker_image = models.CharField(
        max_length=255,
        default="python:3.8-alpine"
    )
