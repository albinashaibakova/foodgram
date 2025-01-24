from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.shortener.serializers import ShortenerSerializer


class ShortLinkView(APIView):
    serializer_class = ShortenerSerializer
    permission_classes = (AllowAny,)

    def get(self, request, **kwargs):
        url = self.request.build_absolute_uri().split('api/')[0]
        slug = kwargs['slug']
        return Response({'short-link': f'{url}{slug}'},
                        status=status.HTTP_200_OK)
