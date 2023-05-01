from django.core.validators import RegexValidator
from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    """Class to store recipe tags in the database."""

    name = models.CharField('Name', max_length=200, unique=True)
    color = models.CharField(
        'Color',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Enter a valid hexadecimal color code.',
            )
        ],
    )
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Class to store ingredients for recipes in the database."""

    name = models.CharField('Name', max_length=200, db_index=True, unique=True)
    measurement_unit = models.CharField('Measurement unit', max_length=50)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class RecipeIngredients(models.Model):
    """Class to store ingredients of a particular recipe in the database."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipeingredients', verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Recipe(models.Model):
    """Class to store recipes in the database."""

    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        RecipeIngredients,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]

    def is_favorited(self, user):
        return self.favorites.filter(user=user).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping.filter(user=user).exists()

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Class to store favorite recipes of a user in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил(а) {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Class to store favorite recipes of a user in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил(а) {self.recipe} в корзину'
