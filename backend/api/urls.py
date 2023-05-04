from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientDisplayViewSet, RecipeManagementViewSet, CurrentUserView,
                    ChangePasswordView, TagDisplayViewSet, UserViewSet)

# Создание маршрутизатора для API
router = DefaultRouter()

router.register('users', UserViewSet) # пользователи
router.register('tags', TagDisplayViewSet) # теги
router.register('ingredients', IngredientDisplayViewSet) # ингредиенты
router.register('recipes', RecipeManagementViewSet)  # рецепты

urlpatterns = [
    # Маршрут для получения данных о текущем пользователе
    path('users/me/', CurrentUserView.as_view()),
    # Маршрут для изменения пароля текущего пользователя
    path('users/set_password/', ChangePasswordView.as_view()),
    # Включение маршрутов, зарегистрированных в маршрутизаторе
    path('', include(router.urls)),
    # Маршруты для аутентификации с использованием токенов
    path('auth/', include('djoser.urls.authtoken')),
]
