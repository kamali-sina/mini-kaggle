from workflows.services.docker import DockerTaskService


class PythonTaskService(DockerTaskService):
    def run_task(self, task_execution):
        task = task_execution.task
        run_container_kwargs = {"image": task.pythontask.docker_image,
                                "volumes": {
                                    "file_path": {"bind": "/run_file.py", "mode": "ro"},
                                    **DockerTaskService.get_accessible_datasets_mount_dict(task)
                                },
                                "environment": self.get_environment(task),
                                "command": "python3 /run_file.py"}
        return self.run_container(task_execution, **run_container_kwargs)
