from django.db.models import F, Count, Q

from data_platform.celery import app

from workflows.models import TaskExecution, WorkflowExecution
from workflows.models.task_dependency import TaskDependencyExecution
from workflows.services.run_task import run_task


@app.on_after_finalize.connect
def setup_run_triggered_workflows_periodic_task(sender, **kwargs):
    sender.add_periodic_task(10, run_triggered_workflows.s(), name='run task dependencies')


@app.task
def run_triggered_workflows():
    triggered_workflows = WorkflowExecution.objects.filter(
        status__in=[WorkflowExecution.StatusChoices.PENDING, WorkflowExecution.StatusChoices.RUNNING]).select_related(
        'workflow').prefetch_related('task_dependency_executions__task_execution__task')
    for workflow_execution in triggered_workflows:
        if workflow_execution.status == WorkflowExecution.StatusChoices.PENDING and \
                workflow_execution.workflow.exceeds_active_execution_limit():
            continue
        run_task_dependencies(workflow_execution)


def run_task_dependencies(workflow_execution):
    executable_task_dependencies = get_executable_task_dependencies(workflow_execution)
    update_workflow_execution_status(workflow_execution, executable_task_dependencies)
    for task_dependency in executable_task_dependencies:
        task_execution = TaskExecution.objects.get(id=run_task(task_dependency.task))
        TaskDependencyExecution.objects.create(workflow_execution=workflow_execution,
                                               task_execution=task_execution)


def get_executable_task_dependencies(workflow_execution):
    succeeded_parents_no_query = Q(parent_tasks__task__in=workflow_execution.task_dependency_executions.filter(
        task_execution__status=TaskExecution.StatusChoices.SUCCESS).values_list('task_execution__task', flat=True))
    return workflow_execution.workflow.task_dependencies.exclude(
        task__in=workflow_execution.task_dependency_executions.values_list('task_execution__task', flat=True)).annotate(
        succeeded_parents_no=Count('parent_tasks', filter=succeeded_parents_no_query),
        parent_tasks_no=Count('parent_tasks', filter=Q())).filter(
        Q(parent_tasks=None) | Q(succeeded_parents_no=F('parent_tasks_no'))).distinct()


def update_workflow_execution_status(workflow_execution, executable_task_dependencies):
    if executable_task_dependencies or workflow_execution.task_dependency_executions.filter(
            task_execution__status__in=[TaskExecution.StatusChoices.RUNNING,
                                        TaskExecution.StatusChoices.PENDING]).exists():
        workflow_execution.status = WorkflowExecution.StatusChoices.RUNNING
    elif workflow_execution.task_dependency_executions.filter(
            task_execution__status=TaskExecution.StatusChoices.FAILED).exists():
        workflow_execution.status = WorkflowExecution.StatusChoices.FAILED
    else:
        workflow_execution.status = WorkflowExecution.StatusChoices.SUCCESS
    workflow_execution.save()


def trigger_workflow(workflow):
    WorkflowExecution.objects.create(workflow=workflow, status=WorkflowExecution.StatusChoices.PENDING)
