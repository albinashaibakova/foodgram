from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def get_recipe_short_link(request, recipe_id):
    long_url = request.build_absolute_uri().split('api')[0]
    slug = get_object_or_404(Recipe, id=request.kwargs['pk']).slug
    return Response({'short-link': f'{long_url}{slug}'})
