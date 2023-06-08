from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet, SubscribeView

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path(r'users/subscriptions/', UserViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path(r'users/<int:user_id>/subscribe/', SubscribeView.as_view(),
         name='subscribe'),
    path('', include(router.urls))
]
