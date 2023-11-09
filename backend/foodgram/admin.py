from django.contrib import admin

from foodgram.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    Cart,
    IngredientInRecipe
)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(IngredientInRecipe)
