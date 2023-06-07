from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscribe
from users.serializers import CustomUserSerializer
from .models import (FavoriteRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'author',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart', 'text',
                  'tags')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(source='ingredient.id')
    name = serializers.SerializerMethodField(source='ingredient.name')
    measurement_unit = serializers.SerializerMethodField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientWriteSerializer(IngredientAmountSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientWriteSerializer(many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, obj):
        if not obj:
            raise serializers.ValidationError(
                'В рецепте не может быть 0 ингредиентов.'
            )
        ingredients = [item['id'] for item in obj]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'Ингредиенты не могут дублироваться.'
                )
        return obj

    def validate_tags(self, obj):
        tags = obj
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError('Теги не могут повторяться.')
            tags_list.append(tag)
        return obj

    def create_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True, source='user.recipe')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(author=obj.author, user=obj.user
                                        ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author',),
                message='Вы уже подписаны на данного пользователя.'
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'Вы не можете оформлять подписки на себя.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance, context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном.'
            ),
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок.'
            ),
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }).data
