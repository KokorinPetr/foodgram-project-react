from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from djoser.views import UserViewSet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from collections import defaultdict


from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)

from recipes.models import (
    Tag, Ingredient, Recipe, FavoriteRecipe, ShoppingCart,
    Subscribe
)

from .mixins import GetOrDeleteViewSet
from .serializers import (
    TagSerializer, RecipeReadSerializer,
    RecipeEditSerializer, IngredientsReadSerializer,
    UserListSerializer, UserCreateSerializer,
    SetPasswordSerializer, RecipeIngredient,
    FavoriteRecipeSerializer, ShoppingCartSerializer,
    SubscribeSerializer
)
from .filters import IngredientsFilter, RecipesFilter

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipesFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = RecipeEditSerializer(
            data=data, context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeEditSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Запрещено изменение чужого контента')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Запрещено удаление чужого контента')
        super().perform_destroy(instance)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = self.request.user
        ingredient_dict = defaultdict(list)
        cart_items = ShoppingCart.objects.filter(user=user)

        for cart_item in cart_items:
            recipe = cart_item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for recipe_ingredient in recipe_ingredients:
                ingredient_info = {
                    'name': recipe_ingredient.ingredient.name,
                    'amount': recipe_ingredient.amount,
                    'measurement_unit':
                        recipe_ingredient.ingredient.measurement_unit
                }
                ingredient_dict[recipe.name].append(ingredient_info)
        text = ""
        for recipe_name, ingredients in ingredient_dict.items():
            text += f"Название рецепта: {recipe_name}\n"
            for ingredient in ingredients:
                text += (
                    f"    {ingredient['name']}, "
                    f"{ingredient['amount']} "
                    f"{ingredient['measurement_unit']},\n"
                )

        filename = f"{user.username}_shopping_list.txt"
        response = HttpResponse(
            text, content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsReadSerializer
    pagination_class = None
    filterset_class = IngredientsFilter


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class FavoriteRecipeViewSet(GetOrDeleteViewSet):
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        user = self.request.user.id
        return FavoriteRecipe.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        u = request.user
        if not FavoriteRecipe.objects.filter(
            user=u, favorite_recipe_id=recipe_id
        ).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            FavoriteRecipe,
            user=request.user,
            favorite_recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(GetOrDeleteViewSet):
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        return ShoppingCart.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        u = request.user
        if not u.shopping_cart.select_related(
                'recipe').filter(
                    recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепта не был добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(GetOrDeleteViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                User,
                id=self.kwargs.get('user_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response({'errors': 'Вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
