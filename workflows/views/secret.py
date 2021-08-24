from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponseRedirect
from workflows.models import Secret
from workflows.forms import SecretForm


class SecretCreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        secret_id = kwargs.get("pk", None)
        secret = Secret.objects.get(id=secret_id)
        if secret.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class SecretListView(LoginRequiredMixin, ListView):
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE
    model = Secret
    template_name = 'secret/list_secret.html'
    context_object_name = 'secrets'

    def get_queryset(self):
        return Secret.objects.filter(creator=self.request.user)


class SecretDetailView(LoginRequiredMixin, SecretCreatorOnlyMixin, DetailView):
    model = Secret
    template_name = 'secret/detail_secret.html'
    context_object_name = 'secret'


class SecretCreateView(LoginRequiredMixin, CreateView):
    model = Secret
    form_class = SecretForm
    template_name = "secret/create_secret.html"

    def form_valid(self, form):
        secret = form.save(commit=False)
        secret.creator = self.request.user
        secret.save()
        messages.success(self.request, 'Your Secret has been created :)')
        success_url = reverse("workflows:detail_secret", args=(secret.pk,))
        return HttpResponseRedirect(success_url)


class SecretDeleteView(LoginRequiredMixin, SecretCreatorOnlyMixin, DeleteView):
    model = Secret

    def get_success_url(self):
        return reverse("workflows:list_secret")
