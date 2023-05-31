from api.serializers import SubscribeSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User
from users.pagination import CustomPagination


class UsersViewSet(UserViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = [CustomPagination]

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=SubscribeSerializer,
            )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Нельзя подписываться на самого себя.'
                )
            if Subscribe.objects.filter(
                user=user,
                author=author,
            ).exists():
                raise exceptions.ValidationError('Подписка уже существует.')
            Subscribe.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Subscribe.objects.filter(
            user=user,
            author=author,
        ).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        subscribe = get_object_or_404(Subscribe, user=user, author=author)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = self.request.user
        authors = user.objects.values('author', 'subscribe')
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
