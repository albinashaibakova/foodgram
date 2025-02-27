from datetime import date

INGREDIENTS_TEMPLATE = '{index}) {name} - {quantity} ({measure_unit})'
RECIPES_TEMPLATE = '{index}) {name}.  @{author}'

MONTHS = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}


def render_shopping_cart(recipes, ingredients):
    """Рендер списка продуктов для рецептов"""
    today = (f'{date.today().day} {MONTHS[date.today().month]} '
             f'{date.today().year}')
    ingredients_to_render = [
        INGREDIENTS_TEMPLATE.format(
            index=index,
            name=ingredient['ingredient__name'].capitalize(),
            quantity=ingredient['quantity'],
            measure_unit=ingredient['ingredient__measurement_unit']
        )
        for index, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_to_render = [
        RECIPES_TEMPLATE.format(
            index=index,
            name=recipe.name,
            author=recipe.author.username
        )
        for index, recipe in enumerate(recipes, start=1)
    ]
    shopping_list = '\n'.join(
        [
            'Список покупок на: {today}'.format(today=today),
            'Продукты',
            *ingredients_to_render,
            'Рецепты',
            *recipes_to_render
        ]
    )
    return shopping_list
