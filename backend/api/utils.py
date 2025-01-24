from django.shortcuts import get_object_or_404
from recipes.models import Recipe


def add_favorite_shopping_cart(request, serializer, *args, **kwargs):
    """Функция для добавления рецепта в избранное или в корзину"""

    user = request.user
    recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])
    serializer = serializer(data={
        'user': user.id,
        'recipe': recipe.id
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def delete_favorite_shopping_cart(request, model, *args, **kwargs):
    """Функция для удаления рецепта из избранного или в корзины"""

    user = request.user
    recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])

    if not model.objects.filter(user=user,
                                recipe=recipe).exists():
        return False
    object = model.objects.filter(user=user, recipe=recipe)
    object.delete()
    return True
