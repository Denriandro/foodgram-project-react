from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

from users.models import Follow

from api.serializers import MiniRecipeSerializer

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка, профиля и текущего юзера."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return Follow.objects.filter(user=current_user, author=obj.id).exists()


class FollowListSerializer(ProfileSerializer):
    """Сериализатор авторов, на которых подписан текущий юзер."""
    recipes = MiniRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj: User):
        return obj.recipes.count()
