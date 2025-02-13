from datetime import date

from django.db.models import Sum
from django.http import FileResponse
from django.utils.text import slugify

from recipes.models import RecipeIngredient



def generate_slug(string):
    string = string.translate(
        str.maketrans(
            "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
        ))
    return slugify(string)


def render_shopping_cart(self, recipes, ingredients):
    """Рендер списка продуктов для рецептов"""

    today = date.today().strftime('%d-%m-%Y')

    ingredients_to_render, recipes_to_render = download_shopping_cart_template(ingredients, recipes)

    shopping_list = '\n'.join(
        [
            'Список покупок на: {today}'.format(today=today),
            ingredients_to_render,
            recipes_to_render
        ]
    )

    filename = f'shopping_list_{today}.txt'
    return shopping_list, filename


def download_shopping_cart_template(ingredients, recipes):
    """Заготовка для списка покупок"""

    ingredients_to_render = ['Ингредиенты']
    recipes_to_render = ['Рецепты']

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

    for index, recipe in enumerate(recipes, start=1):
        recipes_to_render.append(
            '{index}) Рецепт: {recipe_name}. Автор: {recipe_author}'.format(
                index=index,
                recipe_name=recipe[0].capitalize(),
                recipe_author=recipe[1]
            )
        )


    return '\n'.join(ingredients_to_render), '\n'.join(recipes_to_render)
