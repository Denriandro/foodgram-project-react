from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from foodgram.models import (Tag, Ingredient, Recipe,
                             IngredientInRecipe, Favorite, ShoppingCart)
from users.serializers import ProfileSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор RecipeListSerializer."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор list, retrieve рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        serializer = IngredientInRecipeSerializer(ingredients, many=True)
        return serializer.data

    def get_is_add(self, obj, add):
        user = self.context['request'].user
        return (
                user.is_authenticated and
                add.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        return self.get_is_add(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_add(obj, ShoppingCart)


class AddIngredientSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор для RecipeCreateSerializer."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализотор post, update рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = ProfileSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Добавьте хотя бы один тэг!')
        if len(value) != len(set(value)):
            raise ValidationError('Тэги не должны повторяться!')
        return value

    def validate_ingredients(self, value):
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    'В одном рецепте не может быть двух одинаковых '
                    'ингредиентов.'
                )
        return value

    def fill_amount(self, ingredients, recipe):
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        ingredients_dict = {
            ingredient.id: ingredient
            for ingredient in Ingredient.objects.filter(id__in=ingredient_ids)
        }
        ingredients_amount = [
            IngredientInRecipe(
                ingredient=ingredients_dict[ingredient['id']],
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_amount)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.fill_amount(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.fill_amount(recipe=instance, ingredients=ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe', 'add_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Уже в избранном.'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Уже в списке покупок.'
            )
        ]
