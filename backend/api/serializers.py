from collections import OrderedDict

from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag
from users.models import User


class CustomUserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации новых пользователей."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Невозможно создать пользователя с именем "me".'
            )
        return value


class CustomUserInfoSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователях."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class CustomChangePasswordSerializer(
    PasswordSerializer, CurrentPasswordSerializer
):
    """Сериализатор для изменения пароля текущего пользователя."""

    pass


class AuthorSubscriptionSerializer(CustomUserInfoSerializer):
    """Сериализатор для подписки на других авторов рецептов."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        depth = 1

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeLightSerializer(
            recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomTagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class CustomIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientDetailsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов конкретного рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeCreationIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount',)

    def to_representation(self, instance):
        old_repr = super().to_representation(instance)
        new_repr = OrderedDict()
        new_repr['id'] = old_repr['id']
        new_repr['name'] = instance.ingredient.name
        new_repr['measurement_unit'] = instance.ingredient.measurement_unit
        new_repr['amount'] = old_repr['amount']
        return new_repr


class DetailedRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    tags = CustomTagSerializer(read_only=True, many=True)
    author = CustomUserInfoSerializer(read_only=True)
    ingredients = RecipeIngredientDetailsSerializer(read_only=True,
                                                    many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorited(request.user)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_in_shopping_cart(request.user)


class RecipeCreationSerializer(DetailedRecipeSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeCreationIngredientSerializer(many=True)

    def validate(self, attrs):

        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise serializers.ValidationError(
                'Unable to add the same tag multiple times.'
            )

        ingredients = [
            item['ingredient'] for item in attrs['ingredients']]
        if len(ingredients) > len(set(ingredients)):
            raise serializers.ValidationError(
                'Unable to add the same ingredient multiple times.'
            )

        return attrs

    @transaction.atomic
    def set_recipe_ingredients(self, ingredients):
        return [
            RecipeIngredients.objects.get_or_create(
                ingredient=current_ingredient['ingredient'],
                amount=current_ingredient['amount'])[0]
            for current_ingredient in ingredients
        ]

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.ingredients.set(self.set_recipe_ingredients(ingredients))
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        instance.tags.clear()
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.set(self.set_recipe_ingredients(ingredients))
        return instance

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        tag_id_list, tag_list = repr['tags'], []
        for tag_id in tag_id_list:
            tag = get_object_or_404(Tag, id=tag_id)
            serialized_tag = OrderedDict(CustomTagSerializer(tag).data)
            tag_list.append(serialized_tag)
        repr['tags'] = tag_list
        return repr


class RecipeLightSerializer(serializers.ModelSerializer):
    """Serializer for displaying recipes on the subscriptions page."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
