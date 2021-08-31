import os

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.conf import settings
from notebooks.models import Notebook


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


def snippets_list_view(request):
    filenames = next(os.walk('./notebooks/static/notebooks/snippets'), (None, None, []))[2]
    values = [{'name': name, 'value': os.path.splitext(name)[0].replace('_', ' ').capitalize()} for name in filenames]

    return JsonResponse({'success': True, 'results': values})


def snippet_detail_view(request, name):
    with open(f'./notebooks/static/notebooks/snippets/{name}', 'r') as file:
        return JsonResponse({'snippet': file.read()})
