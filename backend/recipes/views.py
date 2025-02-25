from django.shortcuts import redirect
from django.urls import reverse

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError


def get_short_link(request, pk):
    if Recipe.objects(id=pk).exists():
        return redirect(reverse('api:recipe/pk/', args=[pk]))
    raise ValidationError(f'Рецепт по ключу {pk} не найден')
