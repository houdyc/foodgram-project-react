from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import SubscribeView

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('users/subscriptions/',
         SubscribeView.as_view({'get': 'subscriptions'})),
    path('users/<int:author_id>/subscribe/', SubscribeView.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}), name='user-subscribe'),
    path('', include(router.urls))
]
