from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import SubscribeSerializer, SubscribeUserSerializer
from users.models import Subscribe, User
from users.pagination import CustomPagination
from users.serializers import CustomUserSerializer


class UsersViewSet(UserViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    pagination_class = [CustomPagination]

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request, pk=None):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = CustomUserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SubscribeView(UserViewSet):
    queryset = User.objects.all()

    @action(
        methods=['delete', 'post'],
        detail=True,
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        if request.method == 'POST':
            serializer = SubscribeUserSerializer(data=data, context=request)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribe = get_object_or_404(Subscribe, user=user, author=author)
        subscribe.delete()
        return Response('Удалено', status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        followers = User.objects.filter(
            id__in=request.user.follower.all().values('author_id')
        )
        pages = self.paginate_queryset(followers)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
