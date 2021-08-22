import datetime
from celery import shared_task
from notifications.services.send_notifications import send_notification
from workflows.models.task import Task


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
