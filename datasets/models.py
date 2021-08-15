from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

# Create your models here.
from django.core.exceptions import ValidationError

MAX_DATASETS_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_file_size(file):
    filesize = file.size
    if filesize > MAX_DATASETS_FILE_SIZE:
        max_filesize_in_mb = MAX_DATASETS_FILE_SIZE / (1024 * 1024)
        raise ValidationError(f"The maximum file size that can be uploaded is {max_filesize_in_mb}MB")
    else:
        return file


def user_dataset_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/datasets/<filename>
    return f"datasets/{instance.creator.username}/{filename}"


class Tag(models.Model):
    text = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')

    def __str__(self):
        return self.text


class Dataset(models.Model):
    creator = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='datasets')
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    title = models.CharField(max_length=100, null=False, default="No Title")
    description = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to=user_dataset_directory_path,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=["csv"])
        ]
    )
    tags = models.ManyToManyField(Tag, related_name='datasets')
    is_public = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.title)
