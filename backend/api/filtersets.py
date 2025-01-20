import django_filters
from recipes.models import Recipe


class RecipeFilterSet(django_filters.FilterSet):
    username = django_filters.CharFilter(method='filter_author')
    tags = django_filters.CharFilter(method='filter_tags')
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

    def filter_author(self, value):
        return Recipe.objects.filter(author__id=value)

    def filter_tags(self, queryset, name, value):
        lookup = '__'.join([name, 'slug'])
        return queryset.filter(**{lookup: value})

    def filter_is_favorited(self, value):
        return Recipe.objects.filter(is_favorited=bool(int(value)))

    def filter_is_in_shopping_cart(self, value):
        return Recipe.objects.filter(
            is_in_shopping_cart=bool(int(value)))
