import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse

from datasets.views import has_permission
from workflows.models import PythonTask
from notebooks.models import Cell
from notebooks.services.session import make_new_session, SessionService
from notebooks.models import Notebook
from notebooks.models import CODE_SNIPPETS_DIR
from notebooks.forms import ExportNotebookForm, NotebookForm


class NotebookCreatorOnlyMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        notebook = Notebook.objects.get(pk=kwargs["pk"])
        if notebook.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class NotebooksListView(LoginRequiredMixin, generic.ListView):
    model = Notebook
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        return Notebook.objects.filter(creator=self.request.user)


class NotebookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Notebook


class NotebookDeleteView(LoginRequiredMixin, NotebookCreatorOnlyMixin, generic.DeleteView):
    model = Notebook
    success_url = reverse_lazy('notebooks:index')


class NotebookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Notebook
    form_class = NotebookForm
    template_name = 'notebooks/notebook_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        notebook = form.save()
        return HttpResponseRedirect(reverse('notebooks:detail', args=(notebook.id,)))


class ExportNotebook(LoginRequiredMixin, NotebookCreatorOnlyMixin, generic.CreateView):
    model = PythonTask
    form_class = ExportNotebookForm
    template_name = 'notebooks/export.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['notebook'] = get_object_or_404(Notebook, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        task = form.save()
        messages.success(self.request, 'Your task has been created :)')
        return HttpResponseRedirect(reverse('workflows:detail_task', args=(task.id,)))


def snippets_list_view(request):
    _, _, filenames = next(os.walk(CODE_SNIPPETS_DIR))
    values = [
        {
            "name": os.path.splitext(name)[0],
            "value": os.path.splitext(name)[0].replace("_", " ").capitalize(),
        }
        for name in filenames
    ]
    return JsonResponse({"success": True, "results": values})


def snippet_detail_view(request, name):
    with open(f"{CODE_SNIPPETS_DIR}/{name}.py", "r", encoding="utf8") as file:
        return JsonResponse({"snippet": file.read()})


def restart_kernel_view(request, pk):
    notebook = get_object_or_404(Notebook, pk=pk)

    if notebook.session_id:
        session_id = notebook.session_id
    else:
        session_id = make_new_session()

    session_service = SessionService(session_id)
    session_service.restart()
    return JsonResponse({})


def has_notebook_owner_perm(request, notebook_pk):
    notebook = get_object_or_404(Notebook, pk=notebook_pk)
    return notebook.creator.id == request.user.id


def serialize_cell(cell):
    return {"id": cell.id,
            "code": cell.code,
            "cell_status": cell.get_cell_status_display()}


def get_code_from_request(request):
    code = request.POST.get('code', None)
    if not code:
        return ""
    return code


@login_required
@has_permission(has_notebook_owner_perm)
def cell_create_view(request, notebook_pk):
    code = get_code_from_request(request)
    notebook = Notebook.objects.filter(pk=notebook_pk).first()
    if not notebook:
        raise ValidationError("notebook is not valid")
    cell = Cell.objects.create(notebook=notebook, code=code)
    return JsonResponse(serialize_cell(cell))


@login_required
@has_permission(has_notebook_owner_perm)
def cell_update_view(request, notebook_pk, cell_pk):
    # pylint: disable=unused-argument
    cell = get_object_or_404(Cell, pk=cell_pk)
    code = get_code_from_request(request)

    cell.code = code
    cell.save()

    return JsonResponse(serialize_cell(cell))


@login_required
@has_permission(has_notebook_owner_perm)
def cell_delete_view(request, notebook_pk, cell_pk):
    # pylint: disable=unused-argument
    cell = get_object_or_404(Cell, pk=cell_pk)
    cell.delete()

    return JsonResponse({})
