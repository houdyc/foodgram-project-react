from api.models import Recipe
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, author=obj
        ).exists()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'ingredients')


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
