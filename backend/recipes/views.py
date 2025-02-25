from django.shortcuts import redirect

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError


def redirect_short_link(request, pk):
    if Recipe.objects.filter(id=pk).exists():
        scheme = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        return redirect(f'{scheme}://{domain}/recipes/{pk}/')
    raise ValidationError(f'Рецепт по ключу {pk} не найден')
