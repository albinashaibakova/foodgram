from datetime import date

from django.db.models import Sum
from django.http import FileResponse

from recipes.models import RecipeIngredient


def render_shopping_cart(self, recipes, ingredients):

    today = date.today().strftime('%d-%m-%Y')
    ingredients_to_render = []
    recipes_to_render = []
    print(recipes)
    for index, ingredient in enumerate(ingredients, start=1):
        ingredients_to_render.append(
                '{index}) {ingredient__name} - '
                '{quantity} ({measurement_unit})'.format(
                    index=index,
                    ingredient__name=ingredient['ingredient__name'].capitalize(),
                    quantity=ingredient['quantity'],
                    measurement_unit=ingredient['ingredient__measurement_unit']
                )
            )
    ingredients_to_render = '\n'.join(ingredients_to_render)

    for index, recipe in enumerate(recipes, start=1):
        recipes_to_render.append(
                '{index}) Рецепт: {recipe_name}. Автор: {recipe_author}'.format(
                    index=index,
                    recipe_name=recipe[0].capitalize(),
                    recipe_author=recipe[1]
                )
        )

    recipes_to_render = '\n'.join(recipes_to_render)

    shopping_list = '\n'.join(
        [
            'Список покупок на: {today}'.format(today=today),
            'Ингредиенты',
            ingredients_to_render,
            'Рецепты',
            recipes_to_render

        ]
    )

    filename = 'shopping_list.txt'
    return shopping_list, filename
