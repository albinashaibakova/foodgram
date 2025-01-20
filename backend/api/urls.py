from django.urls import include, path
from rest_framework import routers

from api.users.views import UsersViewSet
from api.recipes.views import (IngredientViewSet,
                               RecipeViewSet, TagViewSet)

router = routers.DefaultRouter()


router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('api.shortener.urls', namespace='shortener')),
    path('auth/', include('djoser.urls.authtoken'))
]
