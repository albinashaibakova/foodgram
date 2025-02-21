from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from recipes.views import get_short_link



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('<str:slug>/', get_short_link, name='short_link'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )