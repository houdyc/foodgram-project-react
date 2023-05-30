from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User
from users.pagination import CustomPagination
from users.serializers import SubscriptionSerializer


class UsersViewSet(UserViewSet):
    http_method_names = ('get', 'post')
    pagination_class = [CustomPagination]

    @action(
        http_method_names=('post', 'delete'),
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        if request.method == 'POST':
            author = get_object_or_404(User, id=id)
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            try:
                Subscription.objects.create(user=user, author=author)
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        subscription = Subscription.objects.filter(user=user, author__id=id)
        if not subscription.exists():
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
