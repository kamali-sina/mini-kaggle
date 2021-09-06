from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from workflows.models import Workflow
from workflows.models.task_dependency import TaskDependency
from workflows.forms import TaskDependencyForm


class TaskDependencyDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskDependency

    def get_success_url(self):
        return reverse("workflows:list_workflow")


class TaskDependencyCreateView(LoginRequiredMixin, CreateView):
    model = TaskDependency
    form_class = TaskDependencyForm
    template_name = 'workflows/manage_task_dependencies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        context['task_dependencies'] = workflow.task_dependencies.all().order_by('id')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['workflow_id'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        dependency = form.save(commit=False)
        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])
        dependency.workflow = workflow
        dependency.save()
        form.save_m2m()
        messages.success(self.request, 'Dependency added successfully.')
        success_url = reverse("workflows:manage_dependencies", args=(dependency.workflow.id,))
        return HttpResponseRedirect(success_url)
