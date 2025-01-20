from django.urls import path

from api.shortener.views import ShortLinkView


app_name = 'shortener'
urlpatterns = [
    path('<slug>', ShortLinkView.as_view(), name='short_link'),
]
