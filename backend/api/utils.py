from datetime import date

from django.db.models import Sum
from django.http import FileResponse

from recipes.models import RecipeIngredient


def render_shopping_cart(self, request, *args, **kwargs):

    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(quantity=Sum('amount')).order_by('amount')

    today = date.today().strftime('%d-%m-%Y')
    shopping_list = f'Список покупок на: {today}\n\n'
    for ingredient in ingredients:
        shopping_list += (
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["quantity"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )

    filename = 'shopping_list.txt'
    return FileResponse(shopping_list,
                        filename=filename,
                        content_type='text/plain')
