from django.db.models import Sum
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as rf_filters
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomChangePasswordSerializer,
    CustomUserRegistrationSerializer,
    CustomUserInfoSerializer,
    CustomIngredientSerializer,
    RecipeCreationSerializer,
    DetailedRecipeSerializer,
    CustomTagSerializer,
    AuthorSubscriptionSerializer,
    RecipeLightSerializer,
)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Viewset for managing subscriptions."""

    queryset = Subscription.objects.all()
    serializer_class = AuthorSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Viewset for users registration and displaying."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserRegistrationSerializer
        return CustomUserInfoSerializer


class CurrentUserView(views.APIView):
    """View class for the current user displaying."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserInfoSerializer(
            request.user,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(views.APIView):
    """View class for changing current user's password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CustomChangePasswordSerializer(
            data=request.data,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagDisplayViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for tags display."""

    queryset = Tag.objects.all()
    serializer_class = CustomTagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientDisplayViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for ingredients display."""

    queryset = Ingredient.objects.all()
    serializer_class = CustomIngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeManagementViewSet(viewsets.ModelViewSet):
    """Viewset for recipes."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        author_recipes = Recipe.objects.filter(author=self.request.user)
        if author_recipes.filter(name=serializer.validated_data["name"]).exists():
            raise serializers.ValidationError("A recipe with this name already exists for this author.")
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        author_recipes = Recipe.objects.filter(author=self.request.user).exclude(pk=self.get_object().pk)
        if author_recipes.filter(name=serializer.validated_data["name"]).exists():
            raise serializers.ValidationError("A recipe with this name already exists for this author.")
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreationSerializer
        return DetailedRecipeSerializer


class DownloadShoppingCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        header_font_size = 20
        body_font_size = 15
        header_left_margin = 100
        body_left_margin = 80
        header_height = 770
        body_first_line_height = 740
        line_spacing = 20
        bottom_margin = 100
        bullet_point_symbol = u'\u2022'

        recipes_ingredients = RecipeIngredients.objects.filter(
            recipe__shopping__user=request.user).order_by('ingredient')
        cart = recipes_ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total=Sum('amount'))

        shopping_list = []
        for ingredient in cart:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            line = bullet_point_symbol + f' {name} - {total} {unit}'
            recipes = recipes_ingredients.filter(ingredient__name=name)
            recipes_names = [
                (item.recipe.name, item.amount) for item in recipes]
            shopping_list.append((line, recipes_names))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping.pdf"'
        paper_sheet = canvas.Canvas(response, pagesize=A4)
        registerFont(TTFont('FreeSans', 'FreeSans.ttf'))

        paper_sheet.setFont('FreeSans', header_font_size)
        paper_sheet.drawString(
            header_left_margin, header_height, 'Список покупок')

        paper_sheet.setFont('FreeSans', body_font_size)
        y_coordinate = body_first_line_height
        for ingredient, recipes_names in shopping_list:
            paper_sheet.drawString(body_left_margin, y_coordinate, ingredient)
            y_coordinate -= line_spacing

            for recipe_name in recipes_names:
                if y_coordinate <= bottom_margin:
                    paper_sheet.showPage()
                    y_coordinate = body_first_line_height
                    paper_sheet.setFont('FreeSans', body_font_size)
                recipe_line = f'  {recipe_name[0]} ({recipe_name[1]})'
                paper_sheet.drawString(
                    body_left_margin, y_coordinate, recipe_line)
                y_coordinate -= line_spacing

            if y_coordinate <= bottom_margin:
                paper_sheet.showPage()
                y_coordinate = body_first_line_height
                paper_sheet.setFont('FreeSans', body_font_size)

        paper_sheet.showPage()
        paper_sheet.save()
        return response


class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(recipe=recipe, user=request.user).first()
        if favorite:
            return Response(
                {'errors': 'This recipe is already in your favorites list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = Favorite.objects.create(recipe=recipe, user=request.user)
        serializer = RecipeLightSerializer(
            favorite.recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        favorite = get_object_or_404(Favorite, recipe_id=pk, user=request.user)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated] #

    def create(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = ShoppingCart.objects.filter(recipe=recipe, user=request.user).first()
        if shopping_cart:
            return Response(
                {'errors': 'This recipe is already in your shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart = ShoppingCart.objects.create(recipe=recipe, user=request.user)
        serializer = RecipeLightSerializer(
            shopping_cart.recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        shopping_cart = get_object_or_404(ShoppingCart, recipe_id=pk, user=request.user)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
