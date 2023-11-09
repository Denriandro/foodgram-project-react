from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import CustomUser, Follow
from users.serializers import FollowListSerializer


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(methods=['post'], detail=True)
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowListSerializer(
            follow, data=request.data
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListViewSet(ListModelMixin, GenericViewSet):
    """Вью для списка авторов, на которых подписан текущий пользователь."""
    serializer_class = FollowListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(follower__user=user)
