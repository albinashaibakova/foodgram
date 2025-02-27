import numpy as np

from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def get_histogram(self, cooking_times):
        hists, bins = np.histogram(cooking_times, bins=3)
        return {
            str(i): {
                'range': (round(bins[i]), round(bins[i + 1])),
                'quantity': hists[i]
            }
            for i in range(len(hists))
        }

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        cooking_times = [recipe.cooking_time for recipe in recipes.all()]
        if not cooking_times or min(cooking_times) == max(cooking_times):
            return None
        return [
            (index, f'{ranges["range"][0]} - {ranges["range"][1] - 1} минут '
                    f'({ranges["quantity"]})')
            for index, ranges in self.get_histogram(cooking_times).items()
        ]

    def queryset(self, request, recipes):
        if not self.value():
            return recipes
        return recipes.filter(
            cooking_time__range=self.get_histogram(
                [recipe.cooking_time for recipe in recipes.all()]
            )[self.value()]['range']
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
