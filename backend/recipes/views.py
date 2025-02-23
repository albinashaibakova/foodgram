from django.shortcuts import redirect
from django.urls import reverse

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError


def get_short_link(request, pk):
    if Recipe.objects(id=pk).exists():
        return redirect(reverse('api:recipe-detail', args=[pk]))
    raise ValidationError('Recipe does not exist')
