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
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(read_only=True)
    image = Base64ImageField()
    is_favorite = SerializerMethodField(read_only=True)
    is_shopped = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients', 'is_favorite', 'is_shopped',
                  'image', 'cooking_time', 'id', 'text', 'name')

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'amount',
            amount=models.F('amount_ingredient')
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
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    ingredients = IngredientWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'image', 'ingredients', 'id',
                  'cooking_time', 'name', 'text')

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

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient['amount']

            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient.id,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient['amount']

                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient.id,
                    defaults={'amount': amount}
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )

        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
