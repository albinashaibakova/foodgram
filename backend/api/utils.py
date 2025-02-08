from datetime import date

from django.db.models import Sum
from django.http import FileResponse

from recipes.models import RecipeIngredient


def render_shopping_cart(self, request, recipes, ingredients):



    today = date.today().strftime('%d-%m-%Y')
    shopping_list = f'Список покупок на: {today}\n\n'
    for index, ingredient in enumerate(ingredients, start=1):
        shopping_list += (
            f'{index}) {str(ingredient["ingredient__name"]).capitalize()} - '
            f'{ingredient["quantity"]} '
            f'{str(ingredient["ingredient__measurement_unit"])[:2]}. '
            f'Рецепт - {ingredient["recipe__name"]}\n'
        )

    filename = 'shopping_list.txt'
    return shopping_list, filename
