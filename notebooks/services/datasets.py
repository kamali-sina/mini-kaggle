import os


def get_accessible_datasets(notebook):
    volumes = {}
    for dataset in notebook.accessible_datasets.all():
        volumes.update({dataset.title: f'/datasets/{dataset.title}{os.path.splitext(dataset.file.name)[1]}'})
    return volumes


def get_accessible_datasets_mount_dict(notebook):
    volumes = {}
    for dataset in notebook.accessible_datasets.all():
        volumes.update({dataset.file.path: {
            'bind': f'/datasets/{dataset.title}{os.path.splitext(dataset.file.name)[1]}',
            'mode': 'ro'}})
    return volumes
