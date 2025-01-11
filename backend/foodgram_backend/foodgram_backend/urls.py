from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views
from users.views import UserGetToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/login/', UserGetToken.as_view()),
    path('api/', include('api.urls')),
]
