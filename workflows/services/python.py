import os
import docker

from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.docker import DockerTaskService


class PythonTaskService(DockerTaskService):
    """
    Creates a docker client using from_env
    Runs a new docker container in the background(detach=True) using containers.run
    Customize the docker image by editing the first field of client.containers.run
    """

    def run_task(self, task):
        file_path = os.path.abspath(str(task.pythontask.python_file))
        client = docker.from_env()
        container = client.containers.run(task.pythontask.docker_image, detach=True,
                                          volumes={
                                              file_path: {"bind": "/run_file.py", "mode": "ro"},
                                              **DockerTaskService.get_accessible_datasets_mount_dict(task)
                                          },
                                          environment=self.get_environment(task),
                                          command="python3 /run_file.py")
        DockerTaskExecution.objects.create(task=task, container_id=container.id,
                                           status=TaskExecution.StatusChoices.RUNNING)
