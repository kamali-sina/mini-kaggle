from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Dataset
from .services.csv import read_csv_dataset

from django.views import generic
from .forms import CreateDatasetForm


# Create your views here.


class DatasetIndexView(LoginRequiredMixin, generic.ListView):
    template_name = "datasets/index.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(creator=self.request.user)


@login_required
def dataset_add_dataset(request):
    if request.method == "POST":
        form = CreateDatasetForm(
            request.POST, request.FILES
        )  # there is no instance yet!
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
