from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингредиента.',
        help_text='Введите название ингредиента.'
    )
    count = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Кол-во ингредиента.',
        help_text='Введите кол-во ингредиента.'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'count'),
                name='unique_fields'),
        )
        ordering = ['-id']
        verbose_name = 'Ингридиент.'


class Tag(models.Model):
    name = models.CharField(
        max_length=70,
        null=False,
        unique=True,
        verbose_name='Название тега.'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='ID тега.'
    )
    color = models.CharField(
        'Цветовой HEX-код.',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название рецепта.',
        help_text='Напишите название рецепта.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта.',
        help_text='Автор рецепта.',
    )
    text = models.TextField()
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    cook_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, message='Время должно быть больше 0.'
        )],
        verbose_name='Время приготовления.'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, 'Кол-во должно быть больше 0.'
        )]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient'
            ),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class SelectedRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Selected_unique'
            )
        ]
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном пользователя {self.user}'


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shopping_recipe_user_exists',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} у пользователя {self.user}'
