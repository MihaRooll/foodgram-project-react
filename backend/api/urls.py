from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientDisplayViewSet, RecipeManagementViewSet, CurrentUserView,
                    ChangePasswordView, TagDisplayViewSet, UserViewSet)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagDisplayViewSet)
router.register('ingredients', IngredientDisplayViewSet)
router.register('recipes', RecipeManagementViewSet)

urlpatterns = [
    path('users/me/', CurrentUserView.as_view()),
    path('users/set_password/', ChangePasswordView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
