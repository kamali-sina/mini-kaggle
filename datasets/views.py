import os
import operator
import re
from functools import reduce

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import QueryDict
from django.contrib import messages
from django.db.models import Q
from django.db.models import Count

from datasets.models import Dataset, Tag
from datasets.services.read_csv import read_csv_dataset
from datasets.forms import CreateDatasetForm, UpdateDatasetForm


def has_permission(permission_func):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if permission_func(*args, **kwargs):
                return func(*args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator


def has_dataset_owner_perm(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    return dataset.creator.id == request.user.id


class DatasetListView(LoginRequiredMixin, generic.ListView):
    """datasets list view in which datasets can be filtered by their tags and searched by their titles"""
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE
    template_name = "datasets/datasets.html"
    context_object_name = "datasets_list"
    visibility = 'private'

    def post(self, request):
        return super().get(request)

    def get_queryset(self):
        if not self.get_applying_tags():
            return Dataset.objects.filter(
                self.get_title_search_words_query(), self.get_visibility_query(), self.get_creator_query())
        return Dataset.objects.filter(
            self.get_title_search_words_query(), self.get_visibility_query(), self.get_creator_query()).filter(
            tags__text__in=self.get_applying_tags()).distinct().annotate(
            matching_tags_no=Count('tags')).filter(
            matching_tags_no=len(self.get_applying_tags()))

    def get_visibility_query(self):
        return Q(is_public=True) if self.visibility == 'public' else Q(is_public=False)

    def get_creator_query(self):
        return Q() if self.visibility == 'public' else Q(creator=self.request.user)

    def get_applying_tags(self):
        return self.request.GET.getlist('tag')

    def get_title_search_words_query(self):
        query_list = [Q(title__icontains=search_word) for search_word in self.get_title_search_words()]
        return reduce(operator.or_, query_list, Q())

    def get_title_search_words(self):
        return re.split(r'\s+',
                        self.request.POST.get('search_box', '')) if 'search_box' in self.request.POST else []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visibility'] = self.visibility
        if self.request.user.is_authenticated:
            context['inactive_tags'] = self.request.user.tags.exclude(text__in=self.request.GET.getlist('tag'))
        else:
            context['inactive_tags'] = Tag.objects.filter(datasets__is_public=True).exclude(
                text__in=self.request.GET.getlist('tag')).distinct()
        context['searched'] = self.request.POST.get('search_box', '')
        return context


class DatasetCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dataset
    form_class = CreateDatasetForm
    template_name = 'datasets/upload.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        candidate = form.save(self.request.user)
        success_url = reverse("datasets:detail", args=(candidate.pk,))
        messages.success(self.request, 'Your dataset has been created :)')
        return HttpResponseRedirect(success_url)


@login_required
@has_permission(has_dataset_owner_perm)
def dataset_detail_view(request, pk):
    if request.method == 'GET':
        dataset = get_object_or_404(Dataset, pk=pk)
        context = {'csv': read_csv_dataset(str(dataset.file)),
                   'dataset': dataset}
        return render(request, 'datasets/detail.html', context)
    if request.method == 'PATCH':
        return handle_dataset_patch_method(request, pk)
    if request.method == 'DELETE':
        return handle_dataset_delete_method(pk)
    return HttpResponse("Bad request!", status=400)


def handle_dataset_patch_method(request, pk):
    data = QueryDict(request.body)
    dataset = get_object_or_404(Dataset, pk=pk)

    form = UpdateDatasetForm(data, instance=dataset)
    if not form.is_valid():
        return HttpResponse("Invalid format!", status=400)

    form.save()

    return HttpResponse(f"Dataset {pk} edited successfully", status=200)


def handle_dataset_delete_method(pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    dataset.delete()
    return HttpResponse(f"Dataset {pk} deleted successfully", status=200)


@login_required
@has_permission(has_dataset_owner_perm)
def dataset_download_view(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)

    try:
        with open(dataset.file.path, 'r', encoding="utf-8") as file:
            file_data = file.read()
        response = FileResponse(file_data)
        response['Content-Disposition'] = f'attachment; filename="{dataset.file.name}"'
        return response
    except IOError:
        return HttpResponseNotFound('File not exist')


@method_decorator(has_permission(has_dataset_owner_perm), name='dispatch')
class DatasetUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Dataset
    form_class = UpdateDatasetForm

    def get_success_url(self):
        return reverse('datasets:detail', args=(self.object.pk,))


@method_decorator(login_required, name='dispatch')
@method_decorator(has_permission(has_dataset_owner_perm), name='dispatch')
class DatasetDeleteView(generic.DeleteView):
    model = Dataset
    success_url = reverse_lazy('datasets:index')

    def delete(self, request, *args, **kwargs):
        dataset = self.get_object()
        if dataset.file:
            if os.path.isfile(dataset.file.path):
                os.remove(dataset.file.path)
        return super().delete(self, request, *args, **kwargs)
