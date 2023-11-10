from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeSerializer
)
from foodgram.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    Cart,
)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer


# class FavoriteViewSet():
#     pass
#
#
# class CartViewSet():
#     pass
