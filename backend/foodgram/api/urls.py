from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import SubscriptionsList, SubscribeView

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users/subscriptions', SubscriptionsList)
router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribeView)

urlpatterns = [
    path('', include(router.urls))
]
