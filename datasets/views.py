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
        if dataset.creator.id != request.user.id and not dataset.is_public:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Create your views here.

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "index.html"
    context_object_name = "private_datasets_list"

    def get_queryset(self):
        queryset = Dataset.objects.filter(is_public=False, creator=self.request.user)
        return queryset


class PublicView(LoginRequiredMixin, generic.ListView):
    template_name = "public.html"
    context_object_name = "public_datasets_list"

    def get_queryset(self):
        queryset = Dataset.objects.filter(is_public=True)
        return queryset


class DetailView(LoginRequiredMixin, CreatorOnlyMixin, generic.DetailView):
    model = Dataset
    template_name = "detail.html"


@login_required
def uploadData(request):
    if request.method == "POST":
        form = CreateDatasetForm(request.POST, request.FILES)  # there is no instance yet!
        if form.is_valid():
            file = form.save(commit=False)
            file.creator = request.user
            file.save()
            return HttpResponseRedirect(reverse("datasets:detail", args=(file.id,)))
        return HttpResponse("Invalid format!", status=405)
    elif request.method == "GET":
        form = CreateDatasetForm()
        return render(request, "upload.html", {"form": form})
