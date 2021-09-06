import random

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, CreateView, DeleteView, DetailView, ListView, UpdateView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.defaulttags import register

from workflows.models import Workflow, WorkflowSchedule, WorkflowExecution
from workflows.forms import WorkflowForm, WorkflowScheduleForm
from workflows.services.workflow_run import trigger_workflow

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
    color = ["#" + ''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
    return color


class WorkflowDetailView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, DetailView):
    model = Workflow
    template_name = 'detail_workflow.html'
    context_object_name = 'workflow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workflow = context['workflow']

        # labels for xAxis
        context['execution_timestamps'] = []
        workflow_executions = workflow.workflowexecution_set.all()
        for workflow_execution in workflow_executions:
            context['execution_timestamps'].append(workflow_execution.created_at.strftime("%m/%d/%Y"))

        # chart lines and their data
        context['tasks'] = []
        context['task_executions_run_time'] = {}
        for workflow_task_dependency in workflow.task_dependencies.all():
            task = workflow_task_dependency.task
            context['tasks'].append(task.name)
            task_executions = task.taskexecution_set.all()
            context['task_executions_run_time'][task.name] = []
            for task_execution in task_executions:
                if task_execution.run_time:
                    context['task_executions_run_time'][task.name].append(task_execution.run_time)
                else:
                    context['task_executions_run_time'][task.name].append(0)

        # chart lines colors
        context['colors'] = []
        # pylint: disable=unused-variable
        for i in range(len(context['tasks'])):
            context['colors'].append(random_color())

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


class WorkflowRunView(LoginRequiredMixin, WorkflowCreatorOnlyMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            workflow = get_object_or_404(Workflow, pk=kwargs['pk'])
            trigger_workflow(workflow)
            return HttpResponseRedirect(reverse('workflows:detail_workflow', args=(workflow.pk,)))
        return HttpResponse(status=400)
