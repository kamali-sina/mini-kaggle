from data_platform.settings import MEDIA_ROOT
import tarfile
import docker
import os
from datasets.models import Dataset
from django.contrib.auth.models import User
from io import BytesIO

client = docker.from_env()
container = client.containers.run("python:3.8-alpine", ["sleep", "infinity"], detach=True)
container.exec_run("mkdir wow")
container.exec_run("touch ./wow/fuck.csv")
container.exec_run("touch ./wow/fuck2.csv")
print(container.exec_run("ls")[1].decode('UTF-8'))
print(container.exec_run("ls wow")[1].decode('UTF-8'))


def add_file_to_datasets(file_path, filename):
    user = User.objects.get(id=1)
    path_in_media = "datasets/" + user.username + "/"
    os.makedirs(MEDIA_ROOT + path_in_media, exist_ok=True)
    os.replace(file_path, MEDIA_ROOT + path_in_media + filename)
    Dataset.objects.create(creator=user, file=path_in_media + filename, title="created_by_task")


def run_test(container):
    f = BytesIO()
    bits, stat = container.get_archive("wow")
    for chunk in bits:
        f.write(chunk)
    f.seek(0)
    tar = tarfile.open(fileobj=f)
    tar.extractall()
    tar.close()
    f.close()
    for file in os.listdir('wow'):
        file_path = os.path.abspath('./wow/' + file)
        if (not file_path.endswith('.csv')):
            print(f'{file} is not a supported type')
        add_file_to_datasets(file_path=file_path, filename=file)

run_test(container)