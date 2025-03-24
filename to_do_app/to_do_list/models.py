import time
import hashlib
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_notification  # Импортируем Celery-задачу
from celery.result import AsyncResult

def generate_custom_id(prefix="cat") -> str:
    """Генерирует уникальный идентификатор для категорий."""
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
            self.id = generate_task_id(self.user.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True, db_index=True)

    def __str__(self):
        return f"Profile for {self.user.username} (Telegram ID: {self.telegram_id})"

@receiver(post_save, sender=User) # Создаем UserProfile при создании User
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User) # Сохраняем UserProfile при сохранении User
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Task)
def schedule_notification(sender, instance, created, **kwargs):
    """Планирует отправку уведомления при создании или изменении задачи."""
    if created or instance.due_date != instance.created_at:  # Сравниваем корректно
        # Отменяем предыдущую запланированную задачу (если она была)
        if instance.celery_task_id:
            result = AsyncResult(instance.celery_task_id)
            result.revoke()

        eta = instance.due_date
        task = send_notification.apply_async(args=[instance.pk], eta=eta)
        instance.celery_task_id = task.id
        instance.save() # Сохраняем в БД