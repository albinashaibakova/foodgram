import numpy as np

from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def __init__(self, request, lookup_params, model, model_admin):
        self.cooking_time_ranges = self.get_histogram(model.objects.all())
        super().__init__(request, lookup_params, model, model_admin)

    def get_histogram(self, recipes):
        cooking_time = [recipe.cooking_time for recipe in recipes.all()]
        hists, bins = np.histogram(cooking_time, bins=3)
        histogram_ranges = {
            '0': (round(bins[0]), round(bins[1])),
            '1': (round(bins[1]), round(bins[2])),
            '2': (round(bins[2]), round(bins[3])),
        }
        return histogram_ranges

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        if not recipes:
            return None
        cooking_time = [recipe.cooking_time for recipe in recipes.all()]
        if min(cooking_time) == max(cooking_time):
            return None
        return [
                (index, f'{range[0]} - {range[1]} минут')
                for index, range in enumerate(
                    self.cooking_time_ranges.values()
                )
            ]

    def queryset(self, request, recipes):
        if not self.value():
            return recipes
        return recipes.filter(
            cooking_time__range=self.cooking_time_ranges[self.value()]
        )


class CountFilter(admin.SimpleListFilter):
    def __init__(self, filter_params, *args, **kwargs):
        self.filter_params = filter_params
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        return [
            ('{name}=0'.format(name=self.parameter_name),
             'Нет'),
            ('{name}=1'.format(name=self.parameter_name),
             'Да'),
        ]

    def queryset(self, request, users):
        if not self.value():
            return users
        return users.filter(
            **self.filter_params[self.value()]
        ).distinct()


class HasRecipesFilter(CountFilter):
    title = 'Есть рецепты'
    parameter_name = 'hasrecipes'

    def __init__(self, *args, **kwargs):
        filter_params = {
            'hasrecipes=0': {
                'recipes__isnull': True
            },
            'hasrecipes=1': {
                'recipes__isnull': False
            }
        }
        super().__init__(filter_params, *args, **kwargs)

    def queryset(self, request, users):
        return super().queryset(request, users)


class HasFollowersFilter(CountFilter):
    title = 'Есть подписчики'
    parameter_name = 'hasfollowers'

    def __init__(self, *args, **kwargs):
        filter_params = {
            'hasfollowers=0':
                {'followers__isnull': True},
            'hasfollowers=1':
                {'followers__isnull': False}
        }
        super().__init__(filter_params, *args, **kwargs)

    def queryset(self, request, users):
        return super().queryset(request, users)

class HasFollowingAuthorsFilter(CountFilter):
    title = 'Есть подписки'
    parameter_name = 'hasfollowingauthors'

    def __init__(self, *args, **kwargs):
        filter_params = {
            'hasfollowingauthors=0': {
                'authors__isnull': True
            },
            'hasfollowingauthors=1': {
                'authors__isnull': False
            }
        }
        super().__init__(filter_params, *args, **kwargs)

    def queryset(self, request, users):
        return super().queryset(request, users)
