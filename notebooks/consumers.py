import json
from channels.generic.websocket import WebsocketConsumer

from notebooks.models import Notebook, Cell
from notebooks.services.session import SessionService, make_new_session


class NotebookConsumer(WebsocketConsumer):
    def connect(self):
        # pylint: disable=attribute-defined-outside-init
        self.notebook_id = self.scope['url_route']['kwargs']['notebook_id']
        self.notebook = Notebook.objects.get(pk=self.notebook_id)

        if self.notebook.session_id:
            self.session_id = self.notebook.session_id
        else:
            self.session_id = make_new_session()

        self.session_service = SessionService(self.session_id)

        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        cell_id = text_data_json['cell_id']
        code = text_data_json['code']

        cell = Cell.objects.get(pk=cell_id)
        cell.code = code
        cell.cell_status = Cell.CellStatus.RUNNING
        cell.save()

        result = self.session_service.run_script(code)

        cell.cell_status = Cell.CellStatus.DONE
        cell.save()

        self.send(text_data=json.dumps({
            'cell_id': cell_id,
            'result': result,
        }))

