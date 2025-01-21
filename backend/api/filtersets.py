import django_filters

from recipes.models import Recipe, Tag


class RecipeFilterSet(django_filters.FilterSet):
    username = django_filters.CharFilter(method='filter_author')
    tags = django_filters.MultipleChoiceFilter(field_name='tags__slug',
                                               lookup_expr='slug',
                                               queryset=Tag.objects.all())
    is_favorited = django_filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author',
                  'tags',
                  'is_favorited',
                  'is_in_shopping_cart')

    def filter(self, queryset, name, value):
        if value and self.request.user.id:
            return queryset.filter(**{name: self.request.user})
        return queryset

     def filter_is_favorited(self, queryset, name, value):
        return self.filter(queryset, name, value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter(queryset, name, value)
