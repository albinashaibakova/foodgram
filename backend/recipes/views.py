from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from recipes.models import Recipe


def get_short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(reverse('api:recipe-detail', args=[pk]))
