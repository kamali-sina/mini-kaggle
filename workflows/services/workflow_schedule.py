import logging
from django.db import transaction
from django.utils import timezone
from workflows.models import WorkflowSchedule
from data_platform.celery import app


def run_scheduled_workflow(workflow_schedule):
    if not workflow_schedule.next_run_time:
        workflow_schedule.next_run_time = workflow_schedule.start_time + workflow_schedule.schedule_interval
    if workflow_schedule.next_run_time < timezone.now():
        workflow_schedule.next_run_time = workflow_schedule.next_run_time + workflow_schedule.schedule_interval
        raise NotImplementedError  # call run_workflow celery task
    workflow_schedule.save()


@app.on_after_finalize.connect
def setup_workflows_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10, run_scheduled_workflows.s(), name='run scheduled workflows')


# pylint: disable=broad-except
@app.task
@transaction.atomic
def run_scheduled_workflows():
    workflow_schedules = WorkflowSchedule.objects.select_for_update().filter(paused=False)
    for workflow_schedule in workflow_schedules:
        try:
            run_scheduled_workflow(workflow_schedule)
        except Exception as exc:
            logging.exception(exc)
            print("Problem running workflow with id: " + str(workflow_schedule.workflow.id) + " at the scheduled time.")
