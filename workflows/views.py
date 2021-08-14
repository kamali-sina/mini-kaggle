from django.http import HttpResponseRedirect

from .models import Task
from .forms import TaskForm
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.models import User

class CreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("pk", None)
        task = Task.objects.get(id=task_id)
        if task.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TaskDeleteView(LoginRequiredMixin, CreatorOnlyMixin, DeleteView):
    model = Task

    def get_success_url(self):
        return reverse("workflows:list_task")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'create_task.template'

    def form_valid(self, form):
        candidate = form.save(commit=False)
        candidate.creator = self.request.user
        candidate.save()

        success_url = reverse("workflows:detail_task", args=(candidate.pk,))
        return HttpResponseRedirect(success_url)


class TaskDetailView(LoginRequiredMixin, CreatorOnlyMixin, DetailView):
    model = Task
    template_name = 'detail_task.template'
    context_object_name = 'task'


class TaskListView(LoginRequiredMixin, ListView):
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE
    model = Task
    template_name = 'list_task.template'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(creator=self.request.user)
