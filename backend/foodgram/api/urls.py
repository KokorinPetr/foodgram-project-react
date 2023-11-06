from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet, RecipeViewSet, IngredientViewSet,
    UserViewSet, FavoriteRecipeViewSet, ShoppingCartViewSet,
    SubscribeViewSet,
)
app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteRecipeViewSet,
    basename='favorite')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet,
    basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
