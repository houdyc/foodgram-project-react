from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import SubscribeView, SubscriptionsList

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)


urlpatterns = [
    path(r'users/subscriptions/', SubscriptionsList.as_view({'get': 'list'})),
    path(r'users/<int:user_id>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls))
]
