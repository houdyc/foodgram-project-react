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

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if self.request.user == author or Subscribe.objects.filter(
                user=request.user, author=user_id).exists():
            return Response(
                {'error': 'Вы пытаетесь подписаться на самого '
                 'себя или уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.create(
            author=author, user=self.request.user)
        serializer = SubscribeUserSerializer(
            subscription, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscription = Subscribe.objects.filter(
            user=request.user, author=user_id)
        if subscription.exists():
            subscription.delete()
            return Response({'message': 'Подписка успешно удалена'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'У вас не было такой подписки'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsList(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)
