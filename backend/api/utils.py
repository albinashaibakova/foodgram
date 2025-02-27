from datetime import date

ingredients_template = '{INDEX}) {NAME} - {QUANTITY} ({MEASURE_UNIT})'
recipes_template = '{INDEX}) {NAME}.  @{AUTHOR}'


def render_shopping_cart(recipes, ingredients):
    """Рендер списка продуктов для рецептов"""
    today = date.today().strftime('%d-%m-%Y')
    ingredients_to_render = [
        ingredients_template.format(
            INDEX=index,
            NAME=ingredient['ingredient__name'].capitalize(),
            QUANTITY=ingredient['quantity'],
            MEASURE_UNIT=ingredient['ingredient__measurement_unit']
        )
        for index, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_to_render = [
        recipes_template.format(
            INDEX=index,
            NAME=recipe.name,
            AUTHOR=recipe.author.username
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
