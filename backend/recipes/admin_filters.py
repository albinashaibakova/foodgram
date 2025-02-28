import numpy as np

from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def get_histogram(self, cooking_times):
        hists, bins = np.histogram(cooking_times, bins=3)
        return {
            '0': {
                'range': (round(bins[0]), round(bins[1]) - 1),
                'quantity': hists[0]
            },
            '1': {
                'range': (round(bins[1]), round(bins[2]) - 1),
                'quantity': hists[1]
            },
            '2': {
                'range': (round(bins[2]), round(bins[-1])),
                'quantity': hists[2]
            }
        }
    def get_two_unique_cooking_times(self, unique_cooking_times):
        return {
            str(i): {
                'range': (unique_cooking_times[i], unique_cooking_times[i])
            }
            for i in range(len(unique_cooking_times))
        }

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        cooking_times = [recipe.cooking_time for recipe in recipes.all()]
        unique_cooking_times = sorted(set(cooking_times))
        if len(unique_cooking_times) < 2:
            return None
        if len(unique_cooking_times) == 2:
            self.cooking_time_ranges = self.get_two_unique_cooking_times(
                unique_cooking_times
            )
            return [
                (str(i),
                 f'{time} минут ({recipes.filter(cooking_time=time).count()})')
                for i, time in enumerate(unique_cooking_times)
            ]
        self.cooking_time_ranges = self.get_histogram(cooking_times)
        return [
            (index, f'{ranges["range"][0]} - {ranges["range"][1]} минут '
                    f'({ranges["quantity"]})')
            for index, ranges in self.cooking_time_ranges.items()
        ]

    def queryset(self, request, recipes):
        if not self.value():
            return recipes
        cooking_time_range = self.cooking_time_ranges[self.value()]['range']
        return recipes.filter(
            cooking_time__range=cooking_time_range
        )


class CountFilter(admin.SimpleListFilter):
    def __init__(self, *args, **kwargs):
        self.filter_params = self.get_filter_params()
        super().__init__(*args, **kwargs)

    def get_filter_params(self):
        return {}

    def lookups(self, request, model_admin):
        return [
            ('{name}=0'.format(name=self.parameter_name),
             'Нет'),
            ('{name}=1'.format(name=self.parameter_name),
             'Да'),
        ]

    def queryset(self, request, objects):
        if not self.value():
            return objects
        return objects.filter(
            **self.filter_params[self.value()]
        ).distinct()


class HasRecipesFilter(CountFilter):
    title = 'Есть рецепты'
    parameter_name = 'hasrecipes'

    def get_filter_params(self):
        return {
            'hasrecipes=0': {
                'recipes__isnull': True
            },
            'hasrecipes=1': {
                'recipes__isnull': False
            }
        }


class HasFollowersFilter(CountFilter):
    title = 'Есть подписчики'
    parameter_name = 'hasfollowers'

    def get_filter_params(self):
        return {
            'hasfollowers=0':
                {'followers__isnull': True},
            'hasfollowers=1':
                {'followers__isnull': False}
        }


class HasFollowingAuthorsFilter(CountFilter):
    title = 'Есть подписки'
    parameter_name = 'hasfollowingauthors'

    def get_filter_params(self):
        return {
            'hasfollowingauthors=0': {
                'authors__isnull': True
            },
            'hasfollowingauthors=1': {
                'authors__isnull': False
            }
        }


class IsInRecipesFilter(CountFilter):
    title = 'Есть в рецептах'
    parameter_name = 'isinrecipes'

    def get_filter_params(self):
        return {
            'isinrecipes=0': {
                'recipeingredients__isnull': True
            },
            'isinrecipes=1': {
                'recipeingredients__isnull': False
            }
        }
