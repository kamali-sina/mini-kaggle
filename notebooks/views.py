from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from datasets.views import has_permission
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


def serialize_cell(cell):
    return {"id": cell.id,
            "code": cell.code,
            "cell_status": cell.get_cell_status_display()}


def get_code_from_request(request):
    code = request.POST.get('code', None)
    if not code:
        raise ValidationError("code is required")
    return code


@login_required
@has_permission(has_notebook_owner_perm)
def cell_create_view(request, notebook_pk):
    code = get_code_from_request(request)
    notebook = Notebook.objects.filter(pk=notebook_pk).first()
    if not notebook:
        raise ValidationError("notebook is not valid")
    cell = Cell.objects.create(notebook=notebook, code=code)
    return JsonResponse({"cell": serialize_cell(cell)})


@login_required
@has_permission(has_notebook_owner_perm)
def cell_update_view(request, notebook_pk, cell_pk):
    # pylint: disable=unused-argument
    cell = get_object_or_404(Cell, pk=cell_pk)
    code = get_code_from_request(request)

    cell.code = code
    cell.save()

    return JsonResponse({"cell": serialize_cell(cell)})


@login_required
@has_permission(has_notebook_owner_perm)
def cell_delete_view(request, notebook_pk, cell_pk):
    # pylint: disable=unused-argument
    cell = get_object_or_404(Cell, pk=cell_pk)
    cell.delete()

    return JsonResponse({})
