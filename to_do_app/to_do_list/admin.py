from django.contrib import admin
from .models import Task, Category

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'created_at', 'due_date', 'completed')  # Поля в списке
    list_filter = ('category', 'completed')  # Фильтры справа
    search_fields = ('title',)  # Поиск по названию

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Отображаемые поля
    search_fields = ('name',)  # Поиск по имени
