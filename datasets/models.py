from django.db import models
from django.contrib.auth.models import User


# Create your models here.


def user_dataset_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/datasets/<filename>
    return f"datasets/{instance.creator.username}/{filename}"


class Dataset(models.Model):
    creator = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    title = models.CharField(max_length=100, null=False, default="No Title")
    description = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to=user_dataset_directory_path)
    is_public = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.title)
