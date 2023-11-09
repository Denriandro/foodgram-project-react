from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import TagSerializer, IngredientSerializer
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
    pass


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pass


class RecipeViewSet():
    pass


# class FavoriteViewSet():
#     pass
#
#
# class CartViewSet():
#     pass
