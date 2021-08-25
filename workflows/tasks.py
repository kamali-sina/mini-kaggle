import datetime
import logging

from django.db import transaction

from celery import shared_task
from notifications.services.send_notifications import send_notification
from workflows.models import Task, WorkflowSchedule
from workflows.services.workflow_schedule import run_scheduled_workflow
from data_platform.celery import app


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


# pylint: disable=unused-argument
def run_task_on_failure(self, exc, celery_task_id, args, kwargs, einfo):
    task = Task.objects.get(pk=args[0])
    context = {'task': task,
               'error': einfo.traceback,
               'datetime': datetime.datetime.now()}

    if task.alert_on_failure and task.notification_source:
        send_notification(task.notification_source,
                          'Task failed',
                          'workflows/notification_templates/failure.html',
                          context)


@shared_task(on_failure=run_task_on_failure)
def run_task(task_id):
    raise NotImplementedError
