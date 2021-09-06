from django.http import HttpResponseRedirect

from django.views.generic import DeleteView, DetailView, ListView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register

from workflows.models import Task, TaskExecution
from workflows.forms import TaskForm, TASK_TYPED_FORM_REGISTRY
from workflows.views.workflow import STATUS_CONTEXT_DICT
from workflows.services.docker import task_status_color, get_special_display_fields, get_task_type, DockerTaskService, \
    MarkTaskExecutionStatusOptions, read_task_execution_log_file
from workflows.services.runner import get_service_runner

from workflows.services.run_task import run_task


class CreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("pk", None)
        task = Task.objects.get(id=task_id)
        if task.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TaskExecutionCreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        task_execution_id = kwargs.get("pk", None)
        task_execution = TaskExecution.objects.get(id=task_execution_id)
        if task_execution.task.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TaskDetailView(LoginRequiredMixin, CreatorOnlyMixin, DetailView):
    model = Task
    template_name = 'detail_task.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = context["task"]
        task.get_task_type_display = get_task_type(task)

        task_executions = TaskExecution.objects.filter(task=task)
        task.executions = task_executions
        for task_execution in task_executions:
            task_execution.status_color = task_status_color(task_execution.get_status_display())

        context["special_display_fields"] = get_special_display_fields(task)
        context["accessible_datasets"] = DockerTaskService.get_accessible_datasets_mount_info(task)
        context["mark_options"] = [
            {
                "value": MarkTaskExecutionStatusOptions.FAILED.value,
                "text": "failed",
                "color": "red",
            },
            {
                "value": MarkTaskExecutionStatusOptions.SUCCESS.value,
                "text": "success",
                "color": "green",
            }
        ]

        return context


@login_required
def create_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        typed_form = TASK_TYPED_FORM_REGISTRY[request.POST['task_type']](request.POST, request.FILES)
        if form.is_valid():
            task = form.save()
            return HttpResponseRedirect(reverse('workflows:detail_task', args=(task.id,)))
    else:
        form = TaskForm(user=request.user)
        typed_form = TASK_TYPED_FORM_REGISTRY[Task.DEFAULT_TYPE]()
    return HttpResponse(render(request, 'create_task.html', context={'form': form, 'typed_form': typed_form}))


def get_typed_task_form(request, task_type):
    context = {'form': TASK_TYPED_FORM_REGISTRY[task_type]()}
    return JsonResponse({'form': render_to_string('registration/base_inline_form.html', context=context)})


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
            task.get_task_type_display = get_task_type(task)

        return tasks

    @register.filter
    def get_value(self, key):
        return self.get(key)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = STATUS_CONTEXT_DICT
        return context

def run_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    run_task(task)
    success_url = reverse("workflows:detail_task", args=(task.pk,))
    return HttpResponseRedirect(success_url)


def stop_task_execution_view(request, pk, exec_pk):
    task = get_object_or_404(Task, pk=pk)
    task_runner = get_service_runner(task)
    task_runner.stop_task_execution(
        task_execution_id=exec_pk,
        mark_task_execution_status_as=MarkTaskExecutionStatusOptions(int(request.POST["mark_option"])),
    )

    success_url = reverse("workflows:detail_task", args=(task.pk,))
    return HttpResponseRedirect(success_url)


class TaskExecutionDetailView(LoginRequiredMixin, TaskExecutionCreatorOnlyMixin, DetailView):
    model = TaskExecution
    template_name = 'detail_task_execution.html'
    context_object_name = 'task_execution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_execution = context["task_execution"]
        context["extracted_datasets"] = task_execution.extracted_datasets.all()
        try:
            context["task_execution_have_log"] = True
            context["task_execution_log"] = read_task_execution_log_file(task_execution)
        except FileNotFoundError:
            context["task_execution_have_log"] = False
        return context
