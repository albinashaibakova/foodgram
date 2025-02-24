from django.urls import path

from recipes.views import get_short_link

urlpatterns = [
    path('<int:pk>/', get_short_link, name='short_link')
]
