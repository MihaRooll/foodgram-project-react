from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ChangePasswordView, CurrentUserView, FavoriteViewSet,
                    IngredientDisplayViewSet, RecipeManagementViewSet,
                    ShoppingCartViewSet, SubscribeViewSet, TagDisplayViewSet,
                    UserViewSet)

# Создание маршрутизатора для API
router = DefaultRouter()

router.register('users',
                SubscribeViewSet,
                'subscribers')  # подписки
router.register('users',
                UserViewSet,
                basename='users')  # пользователи
router.register('tags',
                TagDisplayViewSet,
                basename='tags')  # теги
router.register('ingredients',
                IngredientDisplayViewSet,
                basename='ingredients')  # ингредиенты
router.register(
    'recipes',
    FavoriteViewSet,
    basename='favorites')  # избранное
router.register(
    'recipes',
    ShoppingCartViewSet,
    basename='shopping_cart')  # список покупок и его скачивание
router.register('recipes',
                RecipeManagementViewSet,
                basename='recipes')  # рецепты

urlpatterns = [
    # Маршрут для получения данных о текущем пользователе
    path('users/me/', CurrentUserView.as_view()),
    # Маршрут для изменения пароля текущего пользователя
    path('users/set_password/', ChangePasswordView.as_view()),
    # Маршруты для аутентификации с использованием токенов
    path('auth/', include('djoser.urls.authtoken')),
    # Включение маршрутов, зарегистрированных в маршрутизаторе
    path('', include(router.urls)),
]
