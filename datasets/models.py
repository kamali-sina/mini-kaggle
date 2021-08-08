from django.db import models
from django.contrib.auth.models import User


# Create your models here.
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"{instance.creator.username}/{filename}"


class Dataset(models.Model):
    creator = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    description = models.CharField(max_length=200, null=True, default='No description.')
    file = models.FileField(upload_to=user_directory_path)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
