import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from rest_framework.response import Response

from recipes.models import Recipe


def get_short_link(request, slug):
    return HttpResponse(json.dumps({'short-link': request.build_absolute_uri()}))
