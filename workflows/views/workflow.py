import random
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, CreateView, DeleteView, DetailView, ListView, UpdateView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.defaulttags import register

from workflows.models import Workflow, WorkflowExecution, WorkflowSchedule, Task
from workflows.forms import WorkflowForm, WorkflowScheduleForm
from workflows.services.workflow_run import trigger_workflow

RECENT_EXECUTIONS = 12

STATUS_CONTEXT_DICT = {
    WorkflowExecution.StatusChoices.FAILED: {
        "text": "failed",
        "color": "#ff4242",
    },
    WorkflowExecution.StatusChoices.SUCCESS: {
        "text": "success",
        "color": "#68f26f",
    },
    WorkflowExecution.StatusChoices.RUNNING: {
        "text": "running",
        "color": "#53848c",
    },
    WorkflowExecution.StatusChoices.PENDING: {
        "text": "pending",
        "color": "grey",
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
    success_url = reverse_lazy('workflows:list_workflow')


class WorkflowCreateView(LoginRequiredMixin, CreateView):
    model = Workflow
    form_class = WorkflowForm
    template_name = 'create_workflow.html'

    def form_valid(self, form):
        workflow = form.save(commit=False)
        workflow.creator = self.request.user
        workflow.save()
        messages.success(self.request, 'Workflow created successfully.')
        success_url = reverse("workflows:list_workflow")
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


def set_chart_colors(colors, tasks):
    # pylint: disable=unused-variable
    for i in range(len(tasks)):
        color = ["#" + ''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
        colors.append(color)


def generate_chart_context(workflow, context):
    workflow_executions = workflow.workflowexecution_set.all()
    for workflow_execution in workflow_executions:
        context['execution_timestamps'].append(workflow_execution.created_at.strftime("%m/%d/%Y"))

    for workflow_task_dependency in workflow.task_dependencies.all():
        task = workflow_task_dependency.task
        context['tasks'].append(task.name)
        context['task_executions_run_time'][task.name] = []
        for task_execution in task.taskexecution_set.all():
            if task_execution.run_time:
                context['task_executions_run_time'][task.name].append(task_execution.run_time)
            else:
                context['task_executions_run_time'][task.name].append(0)


# pylint: disable=bare-except
def generate_dag_context(context, workflow: Workflow):
    for task_dependency in workflow.task_dependencies.all():
        wfe = workflow.workflowexecution_set.last()
        try:
            te_status = wfe.task_dependency_executions.get(
                task_execution__task=task_dependency.task).task_execution.status
        except:
            te_status = WorkflowExecution.StatusChoices.PENDING
        node_dict = {
            'id': str(task_dependency.task.id),
            'label': task_dependency.task.name,
            'x': 50 * task_dependency.id,
            'y': random.randint(40, 50) * task_dependency.parent_tasks.all().count(),
            'color': STATUS_CONTEXT_DICT[te_status]['color'],
            'size': 2,
        }
        context['nodes'].append(node_dict)
        for task_dependency_parent in task_dependency.parent_tasks.all():
            edge_dict = {
                'id': 'e' + str(task_dependency_parent.task.id) + 't' + str(task_dependency.task.id),
                'source': str(task_dependency_parent.task.id),
                'target': str(task_dependency.task.id),
                'size': 1,
            }
            context['edges'].append(edge_dict)


def get_task_executions_context(workflow, context):
    workflow_executions = workflow.workflowexecution_set.all().order_by('-created_at')[:RECENT_EXECUTIONS]
    workflow_tasks_ids = workflow.task_dependencies.values_list('task', flat=True)
    workflow_tasks = Task.objects.filter(id__in=workflow_tasks_ids)
    for workflow_task in workflow_tasks:
        context['workflow_task_executions'][workflow_task] = []
        for workflow_execution in workflow_executions:
            try:
                task_execution = workflow_execution.task_dependency_executions.get(
                    task_execution__task=workflow_task).task_execution
            except:
                task_execution = {}
            context['workflow_task_executions'][workflow_task].append(task_execution)


class WorkflowDetailView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, DetailView):
    model = Workflow
    template_name = 'detail_workflow.html'
    context_object_name = 'workflow'

    @register.filter
    def get_value(self, key):
        return self.get(key)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workflow = context['workflow']
        context['workflow_executions'] = WorkflowExecution.objects.filter(workflow=workflow).order_by(
            '-created_at__time')[:RECENT_EXECUTIONS]

        context['status'] = STATUS_CONTEXT_DICT

        context['workflow_task_executions'] = {}

        get_task_executions_context(workflow, context)

        # labels for xAxis
        context['execution_timestamps'] = []
        # chart lines and their data
        context['tasks'] = []
        context['task_executions_run_time'] = {}
        # chart lines colors
        context['colors'] = []

        generate_chart_context(workflow, context)
        set_chart_colors(context['colors'], context['tasks'])

        context['nodes'] = []
        context['edges'] = []
        generate_dag_context(context, workflow)

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
    success_url = reverse_lazy("workflows:list_workflow")

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
        return HttpResponseRedirect(self.success_url)


class WorkflowScheduleUpdateView(WorkflowScheduleFormView, UpdateView):
    def get_object(self, queryset=None):
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        return workflow.schedule


class WorkflowRunView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            workflow = get_object_or_404(Workflow, pk=kwargs['pk'])
            trigger_workflow(workflow)
            return HttpResponseRedirect(reverse('workflows:list_workflow'))
        return HttpResponse(status=400)


def workflow_schedule_paused_view(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    data = json.loads(request.body)
    if not request.method == 'POST' or 'paused' not in data or not hasattr(workflow, 'schedule'):
        return HttpResponse(status=400)
    workflow.schedule.paused = data['paused']
    workflow.schedule.save()
    return HttpResponse(status=200)
