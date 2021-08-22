import tarfile
import docker
import os
from datasets.models import Dataset
from django.contrib.auth.models import User

client = docker.from_env()

def add_file_to_datasets(file_path):
    
    Dataset.objects.create(creator=User.objects.get(id=2), file=file_path)

def run_test():
    container = client.containers.run("python:3.8-alpine", ["sleep", "infinity"], detach=True)

    container.exec_run("mkdir wow")
    container.exec_run("touch ./wow/fuck.csv")
    container.exec_run("touch ./wow/fuck2.csv")
    print(container.exec_run("ls")[1].decode('UTF-8'))
    print(container.exec_run("ls wow")[1].decode('UTF-8'))

    f = open('./file.tar', 'wb')
    bits, stat = container.get_archive("wow")
    for chunk in bits:
        f.write(chunk)
    f.close()
    tar = tarfile.open('./file.tar')
    tar.extractall()

    for file in os.listdir('wow'):
        file_path = os.path.abspath('./wow/' + file)
        if (not file_path.endswith('.csv')):
            print(f'{file} is not a supported type')
        add_file_to_datasets(file_path=file_path)