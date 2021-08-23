from django.http import HttpResponseRedirect

from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.shortcuts import render
from workflows.models import Task, PythonTask, DockerTask, TaskExecution
from workflows.forms import TaskForm, PythonTaskForm, DockerTaskForm
from workflows.services.task import task_status_color
from workflows.services.runner import get_service_runner

class CreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("pk", None)
        task = Task.objects.get(id=task_id)
        if task.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TaskDetailView(LoginRequiredMixin, CreatorOnlyMixin, DetailView):
    model = Task
    template_name = 'detail_task.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = context["task"]
        task_runner = get_service_runner(task)
        task.get_task_type_display = task_runner.get_task_type(task)
        task.status = task_runner.task_status(task)

        task_executions = TaskExecution.objects.filter(task=task)
        for task_execution in task_executions:
            task_execution.status = task_runner.task_execution_status(task_execution)
            task_execution.status_color = task_status_color(task_execution.status)
        task.executions = task_executions

        context["display_fields"] = task_runner.get_display_fields(task)
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "create_task.html"

    task_types_data = {
        "docker": {"model": DockerTask, "task_type": Task.TaskTypeChoices.DOCKER, "form_class": DockerTaskForm},
        "python": {"model": PythonTask, "task_type": Task.TaskTypeChoices.PYTHON, "form_class": PythonTaskForm},
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        task_type = self.request.GET.get("type")
        if not task_type:
            context = {
                "task_types": {task_type: reverse("workflows:create_task") + f"?type={task_type}"
                               for task_type in self.task_types_data}
            }
            return render(request, "select_type_for_create_task.html", context)
        return super().get(request, *args, **kwargs)

    def get_form_class(self):
        task_type = self.request.GET.get("type")
        if task_type not in self.task_types_data:
            raise Exception("task type is invalid!")

        task_type_data = self.task_types_data[task_type]
        self.model = task_type_data["model"]
        self.form_class = task_type_data["form_class"]

        return self.form_class

    def form_valid(self, form):
        task_type = self.request.GET.get("type")
        task = form.save(commit=False)
        task.creator = self.request.user
        task.task_type = self.task_types_data[task_type]["task_type"]
        task.save()
        form.save_m2m()
        messages.success(self.request, 'Your task has been created :)')
        success_url = reverse("workflows:detail_task", args=(task.pk,))
        return HttpResponseRedirect(success_url)


class TaskDeleteView(LoginRequiredMixin, CreatorOnlyMixin, DeleteView):
    model = Task

    def get_success_url(self):
        return reverse("workflows:list_task")


class TaskListView(LoginRequiredMixin, ListView):
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE
    model = Task
    template_name = 'list_task.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        tasks = Task.objects.filter(creator=self.request.user)
        for task in tasks:
            task_runner = get_service_runner(task)
            task.status = task_runner.task_status(task)
            task.get_task_type_display = task_runner.get_task_type(task)

        return tasks


def run_task_view(request, pk):
    task = Task.objects.get(pk=pk)

    task_runner = get_service_runner(task)
    task_runner.run_task(task)

    success_url = reverse("workflows:detail_task", args=(task.pk,))
    return HttpResponseRedirect(success_url)
