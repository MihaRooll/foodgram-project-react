from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Class to store recipe tags in the database."""

    name = models.CharField('Name', max_length=200, unique=True)
    color = models.CharField('Color', max_length=7, unique=True)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['pk']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Class to store ingredients for recipes in the database."""

    name = models.CharField('Name', max_length=200, db_index=True)
    measurement_unit = models.CharField('Measurement unit', max_length=200)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['pk']

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        'Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'Ингредиент: {self.ingredient} в кол-ве: {self.amount} '


class Recipe(models.Model):
    """Class to store recipes in the database"""

    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Tags')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    ingredients = models.ManyToManyField(
        RecipeIngredients,
        related_name='recipes',
        verbose_name='Ingredients'
    )
    name = models.CharField('Name', max_length=200)
    image = models.ImageField('Image', upload_to='recipes/')
    text = models.TextField('Text')
    cooking_time = models.PositiveIntegerField('Cooking time')
    pub_date = models.DateTimeField('Publication Date', auto_now_add=True)

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
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
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe} to favorites'


class ShoppingCart(models.Model):
    """Class to store favorite recipes of a user in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe} to shopping cart'
