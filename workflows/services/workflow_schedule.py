import logging

from django.db import transaction
from django.utils import timezone

from data_platform.celery import app

from workflows.models import WorkflowSchedule
from workflows.services.workflow_run import trigger_workflow


@app.on_after_finalize.connect
def setup_trigger_scheduled_workflows_periodic_task(sender, **kwargs):
    sender.add_periodic_task(60, trigger_scheduled_workflows.s(), name='run scheduled workflows')


# pylint: disable=broad-except
@app.task
@transaction.atomic
def trigger_scheduled_workflows():
    workflow_schedules = WorkflowSchedule.objects.select_for_update().filter(paused=False)
    for workflow_schedule in workflow_schedules:
        try:
            trigger_scheduled_workflow(workflow_schedule)
        except Exception as exc:
            logging.exception(exc)
            print("Problem running workflow with id: " + str(workflow_schedule.workflow.id) + " at the scheduled time.")


def trigger_scheduled_workflow(workflow_schedule):
    if not workflow_schedule.next_run_time:
        workflow_schedule.next_run_time = workflow_schedule.start_time + workflow_schedule.schedule_interval
    if workflow_schedule.next_run_time <= timezone.now():
        workflow_schedule.next_run_time = workflow_schedule.next_run_time + workflow_schedule.schedule_interval
        trigger_workflow(workflow_schedule.workflow)
    workflow_schedule.save()
