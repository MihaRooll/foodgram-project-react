from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientDisplayViewSet, RecipeManagementViewSet, CurrentUserView,
                    ChangePasswordView, TagDisplayViewSet, UserViewSet,
                    FavoriteViewSet, ShoppingCartViewSet, DownloadShoppingCartView)

# Создание маршрутизатора для API
router = DefaultRouter()

router.register('users', UserViewSet) # пользователи
router.register('tags', TagDisplayViewSet) # теги
router.register('ingredients', IngredientDisplayViewSet) # ингредиенты
router.register('recipes', RecipeManagementViewSet)  # рецепты
router.register('favorites', FavoriteViewSet, basename='favorites')  # избранное
router.register('shopping_cart', ShoppingCartViewSet, basename='shopping_cart')  # список покупок

urlpatterns = [
    # Маршрут для получения данных о текущем пользователе
    path('users/me/', CurrentUserView.as_view()),
    # Маршрут для изменения пароля текущего пользователя
    path('users/set_password/', ChangePasswordView.as_view()),
    # Включение маршрутов, зарегистрированных в маршрутизаторе
    path('', include(router.urls)),
    # Маршруты для аутентификации с использованием токенов
    path('auth/', include('djoser.urls.authtoken')),
    # Маршрут для скачивания списка покупок в формате PDF
    path('recipes/download_shopping_cart/', DownloadShoppingCartView.as_view(), name='download_shopping_cart')
]
