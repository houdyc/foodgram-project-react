from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.exceptions import ValidationError

from .models import Ingredient, Recipe, Tag, IngredientRecipe
from users.serializers import CustomUserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cook_time')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug', 'id')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'count', 'id')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tag = TagSerializer(many=True, read_only=True)
    ingredient = IngredientSerializer(read_only=True)
    image = Base64ImageField()
    is_selected = SerializerMethodField(read_only=True)
    is_shopped = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'ingredient', 'is_selected', 'is_shopped',
                  'image', 'cook_time', 'id', 'text', 'name')

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'count',
            count=models.F('count_ingredient')
        )
        return ingredients

    def get_sellected(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_shopped(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'count')


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tag = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredient = IngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'image', 'ingredient', 'id', 'cook_time',
                  'name', 'text')

    def get_ingredients(self, obj):
        ingredients = obj
        if ingredients < 1:
            raise ValidationError('В рецепте не может быть 0 ингредиентов.')
        ingredients_list = []
        ingredient = get_object_or_404(Ingredient, id=self.context.id)
        if ingredient in ingredients_list:
            raise ValidationError('Ингредиенты не могут дублироваться.')
        return obj

    def get_tag(self, obj):
        tags = obj
        if not tags:
            raise ValidationError('Нужен хотя бы один тег.')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError('Теги не могут повторяться.')
            tags_list.append(tag)
        return obj


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cook_time'
        )
