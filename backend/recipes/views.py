from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.response import Response

from recipes.models import Recipe


def get_recipe_short_link(request, pk):


    long_url = request.build_absolute_uri()

    my_string = get_object_or_404(Recipe, id=pk).name.translate(
        str.maketrans(
            "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
    ))
    slug = slugify(my_string)
    print(slug)
    long_url = request.build_absolute_uri(slug)
    print(long_url)
    return Response({'short-link': f'{long_url}{slug}'})
