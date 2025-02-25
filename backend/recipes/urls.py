from django.urls import path

from recipes.views import redirect_short_link

urlpatterns = [
    path('s/<int:pk>/', redirect_short_link, name='short_link')
]
