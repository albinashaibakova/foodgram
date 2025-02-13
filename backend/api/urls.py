from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet,
                       RecipeViewSet, TagViewSet,
                       UsersViewSet)

router = routers.DefaultRouter()

app_name = 'api'

router.register('ingredients', IngredientViewSet, 'ingredient')
router.register('recipes', RecipeViewSet, 'recipe')
router.register('tags', TagViewSet, 'tag')
router.register('users', UsersViewSet, 'user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
