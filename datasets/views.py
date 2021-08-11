from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
from .models import Dataset
from .services.csv import read_csv_dataset
from django.views import generic
from .forms import CreateDatasetForm

NUMBER_OF_OBJECTS_PER_PAGE = 10


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
        dataset = form.save(commit=False)  # the file should be there now anyway
        dataset.creator = request.user
        dataset.save()
        return HttpResponseRedirect(reverse("datasets:detail", args=(dataset.id,)))
    elif request.method == "GET":
        form = CreateDatasetForm()
        return render(request, "datasets/upload.html", {"form": form})


def has_permission(permission_func):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if permission_func(*args, **kwargs):
                return func(*args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator


def has_dataset_detail_perm(request, pk):
    # check for dataset public/private access once u add the feature
    dataset = get_object_or_404(Dataset, pk=pk)
    return dataset.creator.id == request.user.id


@login_required
@has_permission(has_dataset_detail_perm)
def dataset_detail_view(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    context = {'csv': read_csv_dataset(str(dataset.file)),
               'dataset': dataset}
    return render(request, 'datasets/detail.html', context)


@login_required
@has_permission(has_dataset_detail_perm)
def dataset_download_view(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    file = open(dataset.file.path, 'rb')
    response = FileResponse(file)
    return response