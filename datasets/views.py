from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Dataset

from django.views import generic
from .forms import CreateDatasetForm


class CreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        dataset_id = kwargs.get("pk", None)
        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Create your views here.


class DatasetIndexView(LoginRequiredMixin, generic.ListView):
    template_name = "index.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(creator=self.request.user)


class DatasetDetailView(LoginRequiredMixin, CreatorOnlyMixin, generic.DetailView):
    model = Dataset
    template_name = "detail.html"


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
        return render(request, "upload.html", {"form": form})
