from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.serializers import FavouriteSerializer
from users.models import Follow, User
from users.pagination import CustomPagination
from users.serializers import FollowSerializer


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = [CustomPagination]

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=FollowSerializer,
            )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribe__user=request.user)
        obj = self.paginate_queryset(queryset)
        serializer = FavouriteSerializer(
            obj,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author_id = pk
        author = get_object_or_404(User, pk=author_id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    data={'detail': 'Нельзя подписаться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    data={'detail': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    data={'detail': 'Вы ещё не подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribe = Follow.objects.filter(user=user, author=author)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
