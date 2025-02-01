from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet,
                               RecipeViewSet, TagViewSet,
                               UsersViewSet)

router = routers.DefaultRouter()


router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:pk>/get-link/', RecipeViewSet.as_view({'get': 'get_short_link'}), name='get-link'),
    path('auth/', include('djoser.urls.authtoken'))
]
