from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SelfUserView,
                    ChangePasswordView, TagViewSet, SubscriptionViewSet)

router = DefaultRouter()
router.register('users', SubscriptionViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('users/me/', SelfUserView.as_view()),
    path('users/set_password/', ChangePasswordView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
