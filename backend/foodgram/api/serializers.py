from django.db import models
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from users.serializers import CustomUserSerializer
from .models import Ingredient, IngredientRecipe, Recipe, Tag


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
    ingredients = IngredientSerializer(read_only=True)
    image = Base64ImageField()
    is_favorite = SerializerMethodField(read_only=True)
    is_shopped = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'ingredients', 'is_selected', 'is_shopped',
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

    def get_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.selected.filter(recipe=obj).exists()

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
    ingredients = IngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'image', 'ingredients', 'id', 'cook_time',
                  'name', 'text')

    def validate_ingredients(self, obj):
        ingredients = obj
        if ingredients < 1:
            raise serializers.ValidationError(
                'В рецепте не может быть 0 ингредиентов.'
            )
        ingredients_list = []
        ingredient = get_object_or_404(Ingredient, id=self.context.id)
        if ingredient in ingredients_list:
            raise serializers.ValidationError(
                'Ингредиенты не могут дублироваться.'
            )
        return obj

    def validate_tag(self, obj):
        tags = obj
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError('Теги не могут повторяться.')
            tags_list.append(tag)
        return obj

    def ingredients_count(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
                for ingredient in ingredients
             ]
        )

    def create(self, validated_data):
        ingredient = self.validated_data.pop('ingredient')
        tag = self.validated_data.pop('tag')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tag)
        self.ingredients_amount(recipe=recipe,
                                ingredients=ingredient)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredients_amount(recipe=instance,
                                ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


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
