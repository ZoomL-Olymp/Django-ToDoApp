import time
import hashlib
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from celery.result import AsyncResult
from to_do_app.celery import app

def generate_custom_id(prefix="cat") -> str:
    """Генерирует уникальный идентификатор для категорий."""
    # Используем secrets.token_hex для большей случайности.
    random_part = secrets.token_hex(8)
    raw_string = f"{prefix}-{int(time.time() * 1000000)}-{random_part}"
    return hashlib.sha256(raw_string.encode()).hexdigest()[:16]

def generate_task_id(user_id: int) -> str:
    """Генерирует уникальный идентификатор для задач, привязанный к пользователю."""
    random_part = secrets.token_hex(8)
    raw_string = f"task-{user_id}-{int(time.time() * 1000000)}-{random_part}"
    return hashlib.sha256(raw_string.encode()).hexdigest()[:16]

class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=16, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_custom_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Task(models.Model):
    id = models.CharField(primary_key=True, max_length=16, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_task_id(self.user.id) # Отдельная функция
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
@receiver(post_save, sender=Task)
def schedule_notification(sender, instance, created, **kwargs):
    """Планирует отправку уведомления при создании или изменении задачи."""
    if created or instance.due_date != instance.created_at:
        # Отменяем предыдущую запланированную задачу (если она была)
        if instance.celery_task_id:
            result = AsyncResult(instance.celery_task_id)
            result.revoke()
        eta = instance.due_date
        task = app.send_task('to_do_list.tasks.send_notification', args=[instance.pk], eta=eta)
        instance.celery_task_id = task.id
        sender.objects.filter(pk=instance.pk).update(celery_task_id=task.id)