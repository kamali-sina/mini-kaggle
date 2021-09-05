import os
from uuid import uuid4
import docker
from django.shortcuts import get_object_or_404
from notebooks.models import Session


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
        self.container = client.containers.run(
                        "m.docker-registry.ir/python:3.8-slim-buster",
                        ["sh", "-c", f"python -i -u <>/{self.fifo_name}"],
                        stdin_open=True,
                        detach=True,
                        volumes={self.fifo_path: {"bind": f"/{self.fifo_name}"}}
                    )
        self.session.container_id = str(self.container.id)
        self.session.status = Session.SessionStatus.RUNNING
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
        for i in range(len(code_lines)):
            if (code_lines[i][0] != '\t'):
                code_lines[i] = '\n' + code_lines[i]
        script = '\n'.join(code_lines) + '\n'
        return script

    def _send_script(self, script):
        """
        Sends users script to session to run

        throws: SessionIsDown exception
        script(str): users script to run
        returns: nothing
        """
        if self.session.status != Session.SessionStatus.RUNNING:
            raise SessionIsDown('Session is down.')
        script = self._get_cleaned_script(script)
        with open(self.fifo_path, 'w', encoding='UTF-8') as fifo_write:
            fifo_write.write(script)

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
        start = log.find(logstart) + len(logstart)
        end = log.find(logend)
        self.session.run_counter = self.session.run_counter + 1
        self.session.save()
        return log[start:end].strip()

    def run_script(self, script):
        """
        Runs the user's script in the session

        returns(str): output of the script
        """
        self._send_script(script)
        return self._get_logs()
