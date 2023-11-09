from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet
from users.views import FollowListViewSet, CustomUserViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet)
router.register(r'subscriptions', FollowListViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
