from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .views import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if Subscribe.objects.filter(user=user, author=obj).exists():
            return True
        return False

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
