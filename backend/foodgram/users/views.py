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


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    @action(detail=True,
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if Subscribe.objects.filter(author=author, user=user).exists():
            return Response({'error': 'Вы уже подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)
        if user == author:
            return Response({'error': 'Невозможно подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscribeSerializer(author, context={'request': request})
        Subscribe.objects.create(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.filter(author=author, user=user).delete()
            return Response('Подписка удалена',
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Вы не подписаны на этого пользователя'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsList(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)
