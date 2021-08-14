from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
from datasets.models import Dataset
from datasets.services.csv import read_csv_dataset
from django.views import generic
from datasets.forms import CreateDatasetForm, EditDatasetInfoForm, DeleteTagForm, AddTagForm
from datasets.services.form_handler import create_dataset_edition_forms_on_get, create_dataset_edition_forms_on_post, \
    submit_dataset_edition_forms
from django.core.exceptions import PermissionDenied

from django.http import QueryDict
from django.contrib.auth.models import User

NUMBER_OF_OBJECTS_PER_PAGE = 10


def has_permission(permission_func):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if permission_func(*args, **kwargs):
                return func(*args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator


def has_dataset_owner_perm(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    return dataset.creator.id == request.user.id


class DatasetIndexView(LoginRequiredMixin, generic.ListView):
    paginate_by = NUMBER_OF_OBJECTS_PER_PAGE
    template_name = "datasets/datasets.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(is_public=False, creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = "private"
        return context


class PublicView(generic.ListView):
    paginate_by = NUMBER_OF_OBJECTS_PER_PAGE
    template_name = "datasets/datasets.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = "public"
        return context


@login_required
def dataset_add_dataset(request):
    if request.method == "POST":
        form = CreateDatasetForm(
            request.POST, request.FILES
        )
        if not form.is_valid():
            return HttpResponse("Invalid format!", status=400)
        dataset = form.save(request.user)  # the file should be there now anyway
        return HttpResponseRedirect(reverse("datasets:detail", args=(dataset.id,)))
    elif request.method == "GET":
        form = CreateDatasetForm()
        return render(request, "datasets/upload.html", {"form": form})


@login_required
@has_permission(has_dataset_owner_perm)
def dataset_detail_view(request, pk):
    if request.method == 'GET':
        dataset = get_object_or_404(Dataset, pk=pk)
        context = {'csv': read_csv_dataset(str(dataset.file)),
                   'dataset': dataset}
        return render(request, 'datasets/detail.html', context)
    if request.method == 'POST':
        return handle_dataset_post_method(request, pk)
    if request.method == 'PATCH':
        return handle_dataset_patch_method(request, pk)
    if request.method == 'DELETE':
        return handle_dataset_delete_method(request, pk)


def handle_dataset_post_method(request, pk):
    user = get_object_or_404(User, pk=request.POST['creator'])
    form = CreateDatasetForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse("Invalid format!", status=400)
    form.save(user, pk=pk)
    return HttpResponse(f'Dataset {pk} created successfully', status=201)


def handle_dataset_patch_method(request, pk):
    data = QueryDict(request.body)
    dataset = get_object_or_404(Dataset, pk=pk)

    info_form = EditDatasetInfoForm(data, instance=dataset)
    add_tag_form = AddTagForm(data, dataset=dataset)
    if not info_form.is_valid() or not add_tag_form.is_valid():
        return HttpResponse(f"Invalid format!", status=400)

    info_form.save()
    add_tag_form.submit()

    return HttpResponse(f"Dataset {pk} edited successfully", status=200)


def handle_dataset_delete_method(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    dataset.delete()
    return HttpResponse(f"Dataset {pk} deleted successfully", status=200)


@login_required
@has_permission(has_dataset_owner_perm)
def dataset_download_view(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    file = open(dataset.file.path, 'rb')
    response = FileResponse(file)
    return response


@login_required
@has_permission(has_dataset_owner_perm)
def edit_dataset_view(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    context = {'pk': pk}
    if request.method == 'GET':
        create_dataset_edition_forms_on_get(context, dataset)
    if request.method == 'POST':
        create_dataset_edition_forms_on_post(context, request.POST, dataset)
        submit_dataset_edition_forms(context)
    return render(request, 'datasets/edit.html', context=context)
