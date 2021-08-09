from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Dataset
from django.views import generic
from .forms import CreateDatasetForm


class PublicOrCreatorMixin(AccessMixin):
    """Verify that the current user is the creator.
        Also see if the requested dataset is public or not."""

    def dispatch(self, request, *args, **kwargs):
        dataset_id = kwargs.get("pk", None)
        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.creator.id != request.user.id and not dataset.is_public:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DatasetIndexView(LoginRequiredMixin, generic.ListView):
    template_name = "datasets.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(is_public=False, creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = "private"
        return context


class PublicView(generic.ListView):
    template_name = "datasets.html"
    context_object_name = "datasets_list"

    def get_queryset(self):
        return Dataset.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = "public"
        return context


class DatasetDetailView(LoginRequiredMixin, PublicOrCreatorMixin, generic.DetailView):
    model = Dataset
    template_name = "detail.html"


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
        return render(request, "upload.html", {"form": form})
