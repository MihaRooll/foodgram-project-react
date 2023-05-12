from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Class for filtering ingredients by their names."""

    name = filters.CharFilter(method='startswith_contains_union_method')

    class Meta:
        model = Ingredient
        fields = ['name']

    def startswith_contains_union_method(self, queryset, name, value):
        if not bool(value):
            return queryset
        startswith_lookup = '__'.join([name, 'istartswith'])
        contains_lookup = '__'.join([name, 'icontains'])
        return queryset.filter(
            Q(**{startswith_lookup: value}) | Q(**{contains_lookup: value})
        ).annotate(
            is_start=ExpressionWrapper(
                Q(**{startswith_lookup: value}),
                output_field=BooleanField()
            )
        ).order_by('-is_start')


class RecipeFilter(FilterSet):
    """Class for filtering recipes."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(method='recipe_boolean_methods')
    is_in_shopping_cart = filters.NumberFilter(
        method='recipe_boolean_methods')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def recipe_boolean_methods(self, queryset, name, value):
        if not bool(value):
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        recipe_ids = [
            r.pk for r in queryset if getattr(r, name)(user) == value]
        if recipe_ids:
            return queryset.filter(pk__in=recipe_ids)
        return queryset.none()
