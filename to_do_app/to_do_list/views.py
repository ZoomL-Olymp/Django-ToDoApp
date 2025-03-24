from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Task, Category, UserProfile
from .serializers import TaskSerializer, CategorySerializer, UserProfileSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
import secrets

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer): # Автоматически устанавливаем пользователя при создании
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all the categories
        for the currently authenticated user.
        """
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth(request):
    telegram_id = request.data.get('telegram_id')
    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = user_profile.user
    except UserProfile.DoesNotExist:
        username = f"user_{secrets.token_hex(8)}"
        user = User.objects.create_user(username=username)
        user.profile.telegram_id = telegram_id
        user.save()


    refresh = RefreshToken.for_user(user)
    tokens = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(tokens, status=status.HTTP_200_OK)