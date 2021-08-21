import docker

from workflows.models import DockerTaskExecution, TaskExecution
from workflows.services.task import TaskService


class DockerTaskService(TaskService):
    def run_task(self, task):
        client = docker.from_env()
        container = client.containers.run(task.dockertask.docker_image, detach=True)
        DockerTaskExecution.objects.create(task=task, container_id=container.id,
                                           status=TaskExecution.StatusChoices.RUNNING)

    def _task_execution_status(self, task_execution):
        StatusChoices = TaskExecution.StatusChoices

        client = docker.from_env()
        container = client.containers.get(task_execution.dockertaskexecution.container_id)
        status = StatusChoices.RUNNING
        if container.status in ["running", "restarting"]:
            status = StatusChoices.RUNNING
        elif container.status == "exited":
            if container.attrs["State"]["ExitCode"] != 0:
                status = StatusChoices.FAILED
            else:
                status = StatusChoices.SUCCESS

            task_execution.status = status
            task_execution.save()

        return status.name
