from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import SubscribeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register(r'users/subscriptions', SubscribeViewSet)


urlpatterns = [
    path('users/<int:author>/subscribe/', SubscribeViewSet.as_view(
        {'post': 'create',
         'delete': 'destroy'})),
    path('', include(router.urls))
]
