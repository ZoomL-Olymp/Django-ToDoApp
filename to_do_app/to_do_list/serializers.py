from rest_framework import serializers
from .models import Task, Category, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id',)


class TaskSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)
    user_task_id = serializers.IntegerField(read_only=True) # Add this

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'celery_task_id', 'user_task_id')

    def validate_due_date(self, value):
        """Проверяет, что дата выполнения не в прошлом."""
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, data):
        """Дополнительная валидация (например, проверка длины заголовка)."""
        if len(data.get('title', '')) > 255:
            raise serializers.ValidationError({"title": "Title is too long (max 255 characters)."})
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = instance.category.id  #  Или  instance.category.name, если хочешь название
        return representation

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Только username

    class Meta:
        model = UserProfile
        fields = ['user', 'telegram_id']
        read_only_fields = ('user',)
