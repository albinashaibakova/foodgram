import json

from django.http import HttpResponse


def get_short_link(request, slug):
    return HttpResponse(json.dumps({'short-link': request.build_absolute_uri()}))
