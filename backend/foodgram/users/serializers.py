from api.models import Recipe
from api.serializers import RecipeShortSerializer
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='user_is_subscribed'
    )

    def user_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField()
    id = serializers.IntegerField(default=serializers.CurrentUserDefault())

    def validate_id(self, value):
        if self.instance.id == value.id:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        return value

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeShortSerializer(
            queryset,
            many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')
