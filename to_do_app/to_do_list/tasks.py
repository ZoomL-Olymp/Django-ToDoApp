from celery import shared_task
from to_do_list.models import Task
from django.utils import timezone

@shared_task
def send_notification(task_id):
    """Отправляет уведомление о задаче."""
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return

    if task.completed:
        return

    ### Отправка уведомления ###