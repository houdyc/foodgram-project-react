from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from api.models import Recipe
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_follow = serializers.SerializerMethodField(
        read_only=True,
        method_name='user_is_followed'
    )

    def user_is_followed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_follow')


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'product_list')


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_follow', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        count_recipes = request.query_params.get('max_recipes')

        if count_recipes is not None:
            recipes = obj.recipes.all()[:(int(count_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return FollowRecipeSerializer(recipes, many=True,
                                      context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
