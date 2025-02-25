from django.shortcuts import redirect

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError


def get_short_link(request, pk):
    scheme = 'https' if request.is_secure() else 'http'
    domain = request.META['HTTP_HOST']
    full_url = f'{scheme}://{domain}/recipes/{pk}/'
    if Recipe.objects.filter(id=pk).exists():
        return redirect(full_url)
    raise ValidationError(f'Рецепт по ключу {pk} не найден')
