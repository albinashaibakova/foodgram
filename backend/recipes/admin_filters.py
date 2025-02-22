import numpy as np

from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def get_histogram(self, recipes):
        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        if min(cooking_time) == max(cooking_time):
            return recipes

        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        hists, bins = np.histogram(cooking_time, bins=3)

        histogram_ranges = {
            '0': (round(bins[0]), round(bins[1])),
            '1': (round(bins[1]), round(bins[2])),
            '2': (round(bins[2]), round(bins[3])),
        }

        return hists, histogram_ranges

    def lookups(self, request, model_admin):

        recipes = model_admin.get_queryset(request)

        if not recipes:
            return None

        return [
            (index, f'{range[0]} - {range[1]} минут')
            for index, range in enumerate(self.get_histogram(recipes)[1].values())
        ]

    def filter_by_range(self, recipes, range):

        return recipes.filter(
            cooking_time__gte=range[0],
            cooking_time__lte=range[1]
        )

    def queryset(self, request, recipes):

        try:
            return self.filter_by_range(
                recipes=recipes,
                range=self.get_histogram(recipes)[1][self.value()]
            )

        except KeyError:
            return recipes


class CountFilter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        return [
            ('{name}=0'.format(name=str(self.__str__())),
             'Нет'),
            ('{name}=1'.format(name=str(self.__str__())),
             'Да'),
        ]

    def __str__(self):
        return str(self.__class__.__name__.lower().replace('filter', ''))

    def queryset(self, request, queryset):
        return queryset


class HasRecipesFilter(CountFilter):
    title = 'Есть рецепты'
    parameter_name = 'hasrecipes'

    filter_params = {
        'hasrecipes=0': {
            'recipes__isnull': True
        },
        'hasrecipes=1': {
            'recipes__isnull': False
        }
    }

    def queryset(self, request, users):
        try:
            return users.filter(
                **self.filter_params[self.value()]
            ).distinct()
        except KeyError:
            return users


class HasFollowersFilter(CountFilter):
    title = 'Есть подписчики'
    parameter_name = 'hasfollowers'
    filter_params = {
            'hasfollowers=0': {
                'followers__isnull': True
            },
            'hasfollowers=1': {
                'followers__isnull': False
            }
        }

    def queryset(self, request, users):
        try:
            return users.filter(
                **self.filter_params[self.value()]
            ).distinct()
        except KeyError:
            return users


class HasFollowingAuthorsFilter(CountFilter):
    title = 'Есть подписки'
    parameter_name = 'hasfollowingauthors'

    filter_params = {
        'hasfollowingauthors=0': {
            'authors__isnull': True
        },
        'hasfollowingauthors=1': {
            'authors__isnull': False
        }
    }

    def queryset(self, request, users):
        try:
            return users.filter(
                **self.filter_params[self.value()]
            ).distinct()
        except KeyError:
            return users
