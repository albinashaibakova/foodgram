from datetime import date

ingredients_template = '{index}) {name} - {quantity} ({measure_unit})'
recipes_template = '{index}) Рецепт: {recipe_name}.  @{recipe_author}'


def render_shopping_cart(self, recipes, ingredients):
    """Рендер списка продуктов для рецептов"""
    today = date.today().strftime('%d-%m-%Y')
    ingredients_to_render = ['Ингредиенты'] + [
        ingredients_template.format(
            index=index,
            name=ingredient['ingredient__name'].capitalize(),
            quantity=ingredient['quantity'],
            measure_unit=ingredient['ingredient__measurement_unit']
        )
        for index, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_to_render = ['Рецепты'] + [
        recipes_template.format(
            index=index,
            recipe_name=recipe[0],
            recipe_author=recipe[1]
        )
        for index, recipe in enumerate(recipes, start=1)
    ]
    shopping_list = '\n'.join(
        [
            'Список покупок на: {today}'.format(today=today),
            '\n'.join(ingredients_to_render),
            '\n'.join(recipes_to_render)
        ]
    )
    filename = f'shopping_list_{today}.txt'
    return shopping_list, filename
