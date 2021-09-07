from notebooks.models import Notebook
from notebooks.services.session import make_new_session, SessionService, FifoIsNotAvailable, SessionIsDown


def set_new_session_for_notebook(notebook):
    session_id = make_new_session()
    notebook.session_id = session_id
    notebook.save()
    return session_id


def get_notebook_session_service(notebook_id):
    notebook = Notebook.objects.get(pk=notebook_id)

    if notebook.session_id:
        try:
            session_id = notebook.session_id
            return SessionService(session_id)
        except SessionIsDown:
            pass
        except FifoIsNotAvailable:
            pass
    # create new session if [notebook have not session] or [Session have problem]
    session_id = set_new_session_for_notebook(notebook)
    return SessionService(session_id)
