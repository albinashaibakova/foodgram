from django.contrib import admin
from django.urls import include, path

from recipes.views import get_short_link



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('<str:slug>/', get_short_link, name='short_link'),
]
