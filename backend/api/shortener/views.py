from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from api.shortener.serializers import ShortenerSerializer


class ShortLinkView(APIView):
    serializer_class = ShortenerSerializer
    permission_classes = (AllowAny,)

    def get(self, request, **kwargs):
        print(request.query_params)
        slug = kwargs['slug']
        return Response({'short-link': slug}, status=status.HTTP_200_OK)