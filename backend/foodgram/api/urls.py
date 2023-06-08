from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import SubscriptionsList, SubscribeView

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('users/subscriptions/', SubscriptionsList.as_view(),
         name='subscriptions'),
    path('users/<int:id>/subscribe/', SubscribeView.as_view(),
         name='subscribe'),
    path('', include(router.urls))
]
