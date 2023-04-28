from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name='Username',
        blank=False,
        unique=True
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Password',
        blank=False,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Email adress',
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='First_name'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Last_name'
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    def __str__(self):
        return f'{self.user} {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Уникальная подписка',
            ),
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
