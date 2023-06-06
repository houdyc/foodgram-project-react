from djoser.views import UserViewSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import SubscribeSerializer
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


class SubscribeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    queryset = User.objects.all()
    serializer_class = SubscribeSerializer
    lookup_field = 'author'
    pagination_class = CustomPagination
    pagination_class.page_size_query_param = 'limit'

    def get_queryset(self):
        if self.action == 'destroy':
            return Subscribe.objects.all()
        return super().get_queryset().filter(
            subscribing=self.request.user.id,
            subscriber=self.request.user.id,
        ).prefetch_related(
            'subscriber',
            'subscribing'
        )

    def create(self, request, *args, **kwargs):
        self.request.data['user'] = self.request.user.id
        self.request.data['author'] = self.kwargs.get('author')
        return super().create(request)
