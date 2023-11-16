from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import RecipesFilter, IngredientFilter
from api.pagination import CustomPagination
from api.permissions import RecipePermission
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from foodgram.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientInRecipe,
)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    # permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermission,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться!'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_messages = []
            for field, errors in e.detail.items():
                error_messages.extend(errors)
            return Response(
                {'error': error_messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def favorite_logic(self, user, recipe):
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        favorite_serializer = RecipeListSerializer(recipe)
        return favorite_serializer.data

    @action(detail=True, methods=('POST', 'DELETE'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            favorite_data = self.favorite_logic(user, recipe)
            return Response(
                favorite_data,
                status=status.HTTP_201_CREATED
            )
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite:
            raise exceptions.ValidationError(
                'The recipe is not in list of favorites'
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def shopping_cart_logic(self, user, recipe):
        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        shopping_cart_serializer = RecipeListSerializer(recipe)
        return shopping_cart_serializer.data

    @action(detail=True, methods=('POST', 'DELETE'))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            shopping_cart_data = self.shopping_cart_logic(user, recipe)
            return Response(
                shopping_cart_data,
                status=status.HTTP_201_CREATED
            )
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not shopping_cart:
            raise exceptions.ValidationError(
                'Нет рецепта.'
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)

        if not shopping_cart_items.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=shopping_cart_items.values('recipe')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = [
            (f'- {ingredient["ingredient__name"]} '
             f'({ingredient["ingredient__measurement_unit"]}) - '
             f'{ingredient["amount"]}')
            for ingredient in ingredients
        ]
        shopping_list = '\n'.join(shopping_list)

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
