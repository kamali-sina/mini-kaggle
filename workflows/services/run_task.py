import datetime
from celery import shared_task
from notifications.services.send_notifications import send_notification
from workflows.models import TaskExecution, Task
from workflows.services.runner import get_service_runner


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
def run_task_in_celery(task_execution_id):
    task_execution = TaskExecution.objects.get(pk=task_execution_id)

    task_execution.status = TaskExecution.StatusChoices.RUNNING
    task_execution.save()
    task_execution.timestamps[str(TaskExecution.StatusChoices.RUNNING.label)] = (datetime.datetime.now()).strftime(
        "%m/%d/%Y, %H:%M:%S")
    runner = get_service_runner(task_execution.task)
    try:
        task_execution_status = runner.run_task(task_execution)
    except:  # pylint: disable=bare-except
        task_execution_status = TaskExecution.StatusChoices.FAILED
        task_execution.timestamps[str(TaskExecution.StatusChoices.FAILED.label)] = (datetime.datetime.now()).strftime(
            "%m/%d/%Y, %H:%M:%S")
    task_execution.status = task_execution_status
    task_execution.timestamps[str(task_execution_status.label)] = (datetime.datetime.now()).strftime(
        "%m/%d/%Y, %H:%M:%S")
    task_execution.save()


def run_task(task):
    task_execution = TaskExecution.objects.create(task=task, status=TaskExecution.StatusChoices.PENDING,
                                                  timestamps={
                                                      str(TaskExecution.StatusChoices.PENDING.label): (
                                                          datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")})
    if not task.timeout or task.timeout.total_seconds() == 0:
        celery_task = run_task_in_celery.delay(task_execution.pk)
    else:
        celery_task = run_task_in_celery.delay(task_execution.pk, time_limit=task.timeout.total_seconds())
    task_execution.celery_task_id = celery_task.id
    task_execution.save()
    return task_execution.pk
