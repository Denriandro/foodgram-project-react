from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.pagination import CustomPagination
from users.models import Follow, CustomUser
from users.serializers import FollowSerializer


class CustomUserViewSet(UserViewSet):

    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    @action(methods=['post'], detail=True)
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListViewSet(ListModelMixin, GenericViewSet):
    """Вью для списка авторов, на которых подписан текущий пользователь."""
    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(follower__user=user)
