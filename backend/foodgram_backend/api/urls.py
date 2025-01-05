from django.urls import include, path
from rest_framework import routers
from users.views import UsersViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()

router.register('users', UsersViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]