import hashlib
import time
from django.db import models
from django.contrib.auth.models import User

def generate_custom_id(user_id: int) -> str:
    """Генерирует уникальный идентификатор"""
    raw_string = f"{user_id}-{int(time.time() * 1000000)}"
    return hashlib.sha256(raw_string.encode()).hexdigest()[:16]  # Усеченный SHA256

class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=16, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:  # Только при создании объекта
            self.id = generate_custom_id(self.user.id)
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

    def save(self, *args, **kwargs):
        if not self.id:  # Только при создании объекта
            self.id = generate_custom_id(self.user.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

