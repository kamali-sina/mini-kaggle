import random

from django.http import HttpResponseRedirect
from django.views.generic import View, CreateView, DeleteView, DetailView, ListView, UpdateView, FormView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.defaulttags import register
from workflows.models import Workflow, WorkflowSchedule, WorkflowExecution
from workflows.forms import WorkflowForm, WorkflowScheduleForm


TASK_EXECUTIONS_RUNTIME = 'task_executions_run_time'
COLORS = 'colors'
TASKS = "tasks"
EXECUTION_TIMESTAMPS = 'execution_timestamps'
STATUS_CONTEXT_DICT = {
    WorkflowExecution.StatusChoices.FAILED: {
        "text": "failed",
        "color": "red",
    },
    WorkflowExecution.StatusChoices.SUCCESS: {
        "text": "success",
        "color": "green",
    },
    WorkflowExecution.StatusChoices.RUNNING: {
        "text": "running",
        "color": "grey",
    },
    WorkflowExecution.StatusChoices.PENDING: {
        "text": "pending",
        "color": "white",
    }
}


class WorkflowCreatorOnlyMixin(AccessMixin):
    """Verify that the current user is the creator."""

    def dispatch(self, request, *args, **kwargs):
        workflow_id = kwargs.get("pk", None)
        workflow = Workflow.objects.get(id=workflow_id)
        if workflow.creator.id != request.user.id:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class WorkflowDeleteView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, DeleteView):
    model = Workflow

    def get_success_url(self):
        return reverse("workflows:list_workflow")


class WorkflowCreateView(LoginRequiredMixin, CreateView):
    model = Workflow
    form_class = WorkflowForm
    template_name = 'create_workflow.html'

    def form_valid(self, form):
        workflow = form.save(commit=False)
        workflow.creator = self.request.user
        workflow.save()
        messages.success(self.request, 'Workflow created successfully.')
        success_url = reverse("workflows:detail_workflow", args=(workflow.pk,))
        return HttpResponseRedirect(success_url)


class WorkflowListView(LoginRequiredMixin, ListView):
    ITEMS_PER_PAGE = 10
    paginate_by = ITEMS_PER_PAGE
    model = Workflow
    template_name = 'list_workflow.html'
    context_object_name = 'workflows'

    def get_queryset(self):
        return Workflow.objects.filter(creator=self.request.user)

    @register.filter
    def get_value(self, key):
        return self.get(key)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = STATUS_CONTEXT_DICT
        return context


def random_color():
    color = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (color(), color(), color())


class WorkflowDetailView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, DetailView):
    model = Workflow
    template_name = 'detail_workflow.html'
    context_object_name = 'workflow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workflow = context['workflow']

        # labels for xAxis
        context[EXECUTION_TIMESTAMPS] = ["31 AUG 2021", "31 AUG 2021"]
        workflow_executions = workflow.workflowexecution_set.all()
        for workflow_execution in workflow_executions:
            context[EXECUTION_TIMESTAMPS].append(workflow_execution.created_at.strftime("%m/%d/%Y"))

        # chart lines (each task is a line)
        context[TASKS] = []
        workflow_tasks= workflow.task_set.all()
        for workflow_task in workflow_tasks:
            context[TASKS].append(workflow_task.name)

        # chart lines colors
        context[COLORS] = []
        # pylint: disable=unused-variable
        for i in range(len(context[TASKS])):
            context[COLORS].append(random_color())

        # chart lines data and yAxis
        context[TASK_EXECUTIONS_RUNTIME] = {}
        for task in workflow_tasks:
            task_executions = task.taskexecution_set.all()
            context[TASK_EXECUTIONS_RUNTIME][task.id] = []
            for task_execution in task_executions:
                if task_execution.run_time:
                    context[TASK_EXECUTIONS_RUNTIME][task.id].append(task_execution.run_time)
                else:
                    context[TASK_EXECUTIONS_RUNTIME][task.id].append(0)

        return context


class WorkflowScheduleRedirectView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, View):
    def dispatch(self, request, *args, **kwargs):
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        if hasattr(workflow, 'schedule'):
            return WorkflowScheduleUpdateView.as_view()(request, *args, **kwargs)
        return WorkflowScheduleCreateView.as_view()(request, *args, **kwargs)


class WorkflowScheduleFormView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, FormView):
    model = WorkflowSchedule
    form_class = WorkflowScheduleForm

    def get_success_url(self):
        return reverse("workflows:detail_workflow", args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context


class WorkflowScheduleCreateView(WorkflowScheduleFormView, CreateView):
    def form_valid(self, form):
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        workflow_schedule = form.save(commit=False)
        workflow_schedule.workflow = workflow
        workflow_schedule.save()
        return HttpResponseRedirect(self.get_success_url())


class WorkflowScheduleUpdateView(WorkflowScheduleFormView, UpdateView):
    def get_object(self, queryset=None):
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        return workflow.schedule
