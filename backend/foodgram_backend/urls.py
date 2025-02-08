from django.contrib import admin
from django.urls import include, path

from recipes.views import get_recipe_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/recipes/<int:pk>/get-link/', get_recipe_short_link),
]
