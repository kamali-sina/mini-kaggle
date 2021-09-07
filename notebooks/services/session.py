import os
from uuid import uuid4
import docker
from django.shortcuts import get_object_or_404
from notebooks.models import Session
from notebooks.services.datasets import get_accessible_datasets_mount_dict

DOCKER_EXITED = 'exited'

class SessionIsDown(Exception):
    pass


class SessionIsUp(Exception):
    pass


class FifoIsNotAvailable(Exception):
    pass


def make_new_session():
    """
    Makes a new session model

    returns(int): created session id
    """
    session = Session.objects.create(uuid=str(uuid4()), container_id=None)
    return session.id

class SessionService:
    """
    Class for running and communicating with a python session
    """
    LOGSTART = 's_%s_%s'
    LOGEND = 'e_%s_%s'

    def __init__(self, session_id):
        self.session = get_object_or_404(Session, pk=session_id)
        self.fifo_name = f'session_{self.session.id}_fifo'
        self.fifo_path = f'/tmp/{self.fifo_name}'
        self.container = None
        if self.session.status != Session.SessionStatus.RUNNING:
            self.start()
        else:
            self._load_session()

    def _make_fifo(self):
        """
        Makes fifo for interacting with the container
        """
        if os.path.exists(self.fifo_path):
            os.remove(self.fifo_path)
        os.mkfifo(self.fifo_path)

    def _check_fifo(self):
        """
        Checks if fifo is available for load session

        throws: FifoIsNotAvailable if the bounded fifo is not available
        """
        if not os.path.exists(self.fifo_path):
            raise FifoIsNotAvailable("trying to load from session that it's fifo is deleted!")

    def _load_session(self):
        """
        Loads container if it exists, makes one if no container id is available

        throws: docker.errors.APIError if container id is invalid
        """
        if not self.session.container_id:
            self.start()
        self._check_fifo()
        self._update_container()

    def _update_container(self):
        """
        Updates the self.container object
        """
        client = docker.from_env()
        self.container = client.containers.get(self.session.container_id)

    def start(self):
        """
        starts the session if down

        returns: nothing
        """
        if self.session.status == Session.SessionStatus.RUNNING:
            return
        self._make_fifo()
        client = docker.from_env()

        volumes = {}
        if self.session.notebook:
            volumes.update(get_accessible_datasets_mount_dict(self.session.notebook))
        volumes.update({self.fifo_path: {"bind": f"/{self.fifo_name}"}})

        self.container = client.containers.run(
            "m.docker-registry.ir/python:3.8-slim-buster",
            ["sh", "-c", f"python -i -u <>/{self.fifo_name}"],
            stdin_open=True,
            detach=True,
            volumes=volumes
        )
        self.session.container_id = str(self.container.id)
        self.session.status = Session.SessionStatus.RUNNING
        self.session.run_counter = 1
        self.session.save()

    def stop(self):
        """
        ends the session if up

        returns: nothing
        """
        if self.session.status != Session.SessionStatus.RUNNING:
            return
        self.container.stop()
        self.session.status = Session.SessionStatus.NOTRUNNING
        self.session.save()

    def restart(self):
        """
        restarts the session

        returns: nothing
        """
        self.stop()
        self.start()

    def _add_uuids(self, script):
        """
        Adds uuids to the start and end of the script for log identification

        script(str): users script to run
        returns(str): updated script
        """
        start = f"print('{self.LOGSTART%(self.session.uuid, self.session.run_counter)}')\n"
        end = f"\n\nprint('{self.LOGEND%(self.session.uuid, self.session.run_counter)}')\n"
        return start + script + end

    def _get_cleaned_script(self, script):
        """
        Cleans input script for python shell

        script(str): users script to run
        returns(str): updated script
        """
        script = self._add_uuids(script)
        splitted_script = script.split('\n')
        code_lines = []
        for line in splitted_script:
            if line.strip() != '':
                code_lines.append(line)
        for i, line in enumerate(code_lines):
            if line[0] != '\t' and line[0] != ' ':
                code_lines[i] = '\n' + line
        script = '\n'.join(code_lines) + '\n'
        return script

    def _send_script(self, script):
        """
        Sends users script to session to run

        script(str): users script to run
        returns: nothing
        """
        script = self._get_cleaned_script(script)
        with open(self.fifo_path, 'w', encoding='UTF-8') as fifo_write:
            fifo_write.write(script)

    def _run_session_checks(self):
        """
        Checks if the session is up and its container is intact

        throws: SessionIsDown exception
        """
        if self.session.status != Session.SessionStatus.RUNNING:
            raise SessionIsDown('Session is down.')
        container_state = self.container.attrs["State"]
        if container_state["Status"] == DOCKER_EXITED:
            raise SessionIsDown('Session container has exited.')

    def _get_cleaned_logs(self, log, logstart, logend):
        """
        Tries its best to get the full log even during errors.

        log(str): full log of the container
        logstart(str): start id of the log
        logend(str): end id of the log
        returns(str): cleaned log
        """
        start = log.find(logstart) + len(logstart)
        normal_log = log[start:].replace(logend, '')
        if normal_log.strip() != '' or self.session.run_counter == 1:
            return normal_log
        lastlogend = self.LOGEND%(self.session.uuid, self.session.run_counter - 1)
        start = log.find(lastlogend) + len(lastlogend)
        return log[start:].replace(logstart, '').replace(logend, '')

    def _get_logs(self):
        """
        Gets the logs of the last executed script

        returns(str): output of the run
        """
        logstart = self.LOGSTART%(self.session.uuid, self.session.run_counter)
        logend = self.LOGEND%(self.session.uuid, self.session.run_counter)
        log = self.container.logs().decode('UTF-8')
        while log.find(logstart) == -1 or log.find(logend) == -1:
            log = self.container.logs().decode('UTF-8')
        cleaned_log = self._get_cleaned_logs(log, logstart, logend)
        self.session.run_counter = self.session.run_counter + 1
        self.session.save()
        return cleaned_log

    def run_script(self, script):
        """
        Runs the user's script in the session

        throws: SessionIsDown exception
        returns(str): output of the script
        """
        self._update_container()
        self._run_session_checks()
        self._send_script(script)
        return self._get_logs()
