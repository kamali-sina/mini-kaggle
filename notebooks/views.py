from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy
from django.http import JsonResponse

from notebooks.models import Notebook, Cell


class NotebookCreatorOnlyMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        notebook = Notebook.objects.get(pk=kwargs['pk'])
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


def has_notebook_owner_perm(request, notebook_id, *args, **kwargs):
    notebook = get_object_or_404(Notebook, pk=notebook_id)
    return notebook.creator.id == request.user.id


def cell_serializer(cell):
    return {"id": cell.id,
            "code": cell.code,
            "cell_status": cell.get_cell_status_display(),
            "result": cell.result}


def get_code_from_request(request):
    code = request.POST.get('code', None)
    if not code:
        raise Exception("code is required")
    return code


def get_notebook_from_request(request):
    notebook_id = request.POST.get('notebook', None)
    if not notebook_id:
        raise ValidationError("notebook is required")

    notebooks = Notebook.objects.filter(pk=notebook_id)
    if not notebooks:
        raise ValidationError("notebook_id is not valid")

    notebook = notebooks[0]
    if not has_notebook_owner_perm(request, notebook.id):
        raise PermissionDenied()

    return notebook


@login_required
def cell_create_view(request):
    notebook = get_notebook_from_request(request)
    code = get_code_from_request(request)

    cell = Cell.objects.create(notebook=notebook, code=code)
    return JsonResponse({
        "message": "successful",
        "data": {"cell": cell_serializer(cell)}
    })


@login_required
def cell_update_view(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    get_notebook_from_request(request)
    code = get_code_from_request(request)

    cell.code = code
    cell.save()

    return JsonResponse({
        "message": "successful",
        "data": {"cell": cell_serializer(cell)}
    })


@login_required
def cell_delete_view(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    get_notebook_from_request(request)
    cell.delete()

    return JsonResponse({
        "message": "successful",
        "data": None})
