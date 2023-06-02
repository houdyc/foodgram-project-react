from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.pagination import CustomPagination
from users.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly

from .filters import IngredientFilter, RecipeFilter
from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingList, Tag
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    def create_or_delete(self, request, pk, model, serializer, message):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            data = {
                'user': user.id,
                'recipe': recipe.id
            }
            serializer = serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not instance.exists():
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.create_or_delete(
            request=request,
            pk=pk,
            model=FavoriteRecipe,
            serializer=FavoriteSerializer,
            message={'errors': 'Рецепта нет в избранном!'}
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.create_or_delete(
            request=request,
            pk=pk,
            model=ShoppingList,
            serializer=ShoppingCartSerializer,
            message={'errors': 'Рецепта нет в списке покупок!'}
        )

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = Recipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(total=Sum('ingredients_list__amount')).order_by('-total')
        shopping_list = ['Список покупок: ', ]
        for num, item in enumerate(ingredients):
            shopping_list.append(
                f'{num + 1}. {item["name"]} = '
                f'{item["total"]} {item["measurement"]}'
            )
        text = '\n'.join(shopping_list)
        filename = 'foodgram_shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class PermissionAndPaginationMixin:
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class TagViewSet(PermissionAndPaginationMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(PermissionAndPaginationMixin,
                        viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
