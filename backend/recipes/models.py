from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=4,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        null=True,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        null=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время готовки, мин.',
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Время создания'
    )

    class Meta:
        ordering = ('-creation_date',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        null=True,
        validators=[MinValueValidator(1),
                    MaxValueValidator(10000)
                    ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='Уникальный ингредиент в рецепте',
            ),
        )

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts'
    )

    class Meta:
        verbose_name = "Корзина рецептов"
        verbose_name_plural = "Корзины рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальный рецепт в корзине',
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriter'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriting'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальный рецепт в избранном',
            ),
        ]
