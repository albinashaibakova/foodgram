from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag


class RecipeFilterSet(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                        to_field_name='slug',
                                        queryset=Tag.objects.all())
    is_favorited = filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author',
                  'tags',
                  'is_favorited',
                  'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
