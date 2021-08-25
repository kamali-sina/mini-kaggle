from django.utils import timezone


def run_scheduled_workflow(workflow_schedule):
    if not workflow_schedule.next_run_time:
        workflow_schedule.next_run_time = workflow_schedule.start_time + workflow_schedule.schedule_interval
    if workflow_schedule.next_run_time < timezone.now():
        workflow_schedule.next_run_time = workflow_schedule.next_run_time + workflow_schedule.schedule_interval
        raise NotImplementedError  # call run_workflow celery task
    workflow_schedule.save()
