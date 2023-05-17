from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLES = {
        (USER, 'user'),
        (ADMIN, 'admin'),
    }
    username = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            UnicodeUsernameValidator(message='Некорректное имя пользователя')
        ]
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
        validators=[
            EmailValidator(message='Некорректный email')
        ]
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Имя',
    )

    second_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Фамилия',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER,
        verbose_name='Роль',
    )
    password = models.CharField(
        max_length=150,
        help_text='Введите пароль',
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='uniq_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_following',
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.author}'
