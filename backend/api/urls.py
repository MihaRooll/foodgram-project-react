from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Создание маршрутизатора для API
router = DefaultRouter()

# Регистрация маршрутов для различных представлений
router.register('users', views.UserViewSet)  # пользователи
router.register('tags', views.TagDisplayViewSet)  # теги
router.register('ingredients', views.IngredientDisplayViewSet)  # ингредиенты
router.register('recipes', views.RecipeManagementViewSet)  # рецепты
router.register(
    'favorites', views.FavoriteViewSet, basename='favorite')  # избранное
router.register(
    'shopping_cart',
    views.ShoppingCartViewSet, basename='shopping_cart')  # корзина

urlpatterns = [
    # Маршрут для получения данных о текущем пользователе
    path('users/me/', views.CurrentUserView.as_view()),
    # Маршрут для изменения пароля текущего пользователя
    path('users/set_password/', views.ChangePasswordView.as_view()),
    # Включение маршрутов, зарегистрированных в маршрутизаторе
    path('', include(router.urls)),
    # Маршруты для аутентификации с использованием токенов
    path('auth/', include('djoser.urls.authtoken')),
]
