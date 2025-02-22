from django_filters.rest_framework import filters, FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilterSet(FilterSet):
    """Фильтр для рецептов"""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_is_favorited(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(recipes_favorite__user=self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(recipes_shoppingcart__user=self.request.user)
        return recipes
