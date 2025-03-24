import time
import hashlib
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)  # Added user field

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
    user_task_id = models.PositiveIntegerField(null=True, blank=True) # ID for user convenience

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_task_id(self.user.id)
        if not self.user_task_id:  # Only set on creation
            max_id = Task.objects.filter(user=self.user).aggregate(models.Max('user_task_id'))['user_task_id__max']
            self.user_task_id = (max_id or 0) + 1 # Increment, handle None
        super().save(*args, **kwargs)  # Call super *after* setting user_task_id

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True, db_index=True)

    def __str__(self):
        return f"Profile for {self.user.username} (Telegram ID: {self.telegram_id})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Task)
def schedule_notification(sender, instance, created, **kwargs):
    """Планирует отправку уведомления при создании или изменении задачи."""
    from .tasks import send_notification  # Import inside the function

    if created or instance.due_date != instance.created_at:
        # Revoke any existing task *before* scheduling a new one
        if instance.celery_task_id:
            result = AsyncResult(instance.celery_task_id)
            if result.state not in ('PENDING', 'STARTED', 'RETRY'): # Revoke only pending
                print(f"Task {instance.celery_task_id} is not in pending state. State is {result.state}")
            result.revoke()

        eta = instance.due_date
        task = send_notification.apply_async(args=[instance.pk], eta=eta)
        instance.celery_task_id = task.id
        # instance.save()  <-- REMOVE THIS LINE!  NO DOUBLE SAVE!