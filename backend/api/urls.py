from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import FollowListViewSet, CustomUserViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')
router.register(r'users/subscriptions', FollowListViewSet,
                basename='subscriptions')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
