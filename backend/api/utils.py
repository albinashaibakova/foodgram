from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def add_favorite_shopping_cart(request, serializer, *args, **kwargs):
    user = request.user
    recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])
    serializer = serializer(data={
        'user': user.id,
        'recipe': recipe.id
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data

def delete_favorite_shopping_cart(request, model, *args, **kwargs):
    user = request.user
    recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])

    if not model.objects.filter(user=user,
                                recipe=recipe).exists():
        return False
    else:
        object = model.objects.filter(user=user,
                                      recipe=recipe)
        object.delete()
        return True
