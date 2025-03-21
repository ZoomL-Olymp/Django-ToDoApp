from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)  # Генерирует /api/tasks/
router.register(r'categories', CategoryViewSet)  # Генерирует /api/categories/

urlpatterns = [
    path('', include(router.urls)),  # Включаем маршруты API
]
