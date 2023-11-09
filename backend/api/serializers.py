from rest_framework import serializers

from foodgram.models import Tag, Ingredient, Recipe

# User = get_user_model()


class MiniRecipeSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
