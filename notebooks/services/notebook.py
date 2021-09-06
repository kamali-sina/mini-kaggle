from notebooks.models import Notebook
from notebooks.services.session import make_new_session, SessionService


def get_notebook_session_service(notebook_id):
    notebook = Notebook.objects.get(pk=notebook_id)

    if notebook.session_id:
        session_id = notebook.session_id
    else:
        session_id = make_new_session()
        notebook.session_id = session_id
        notebook.save()

    return SessionService(session_id)
