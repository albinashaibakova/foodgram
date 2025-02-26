from django.shortcuts import redirect

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError


def redirect_short_link(request, pk):
    if Recipe.objects.filter(id=pk).exists():
        return redirect(f'/recipes/{pk}/')
    raise ValidationError(f'Рецепт по ключу {pk} не найден')
