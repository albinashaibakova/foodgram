from django.contrib import admin
from django.db.models import Count, Avg
import numpy as np

class CookingTimeFilter(admin.SimpleListFilter):

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def get_histogram(self, recipes):
        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        if min(cooking_time) == max(cooking_time):
            return recipes

        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        hists, bins = np.histogram(cooking_time, bins=3)

        histogram_ranges = [
            f'{bins[0]} - {round(bins[1])}',
            f'{round(bins[1])} - {round(bins[2])}',
            f'{round(bins[2])} - {bins[3]}',
        ]

        return hists, histogram_ranges

    def lookups(self, request, model_admin):

        recipes = model_admin.get_queryset(request)

        if not recipes:
            return None

        return [
            (str(index), f'{range_recipes} ({self.get_histogram(recipes)[1][index]})')
            for index, range_recipes in enumerate(self.get_histogram(recipes)[1])
        ]

    def filter_by_range(self, request, model_admin, range):
        recipes = model_admin.get_queryset(request)
        return recipes.filter(cooking_time__gte=range[0], cooking_time__lte=range[1])

    def queryset(self, request, recipes):
        filt_cooking_time = request.GET.get('cooking_time')
        print(filt_cooking_time)
        print(type(self.value()))

        if filt_cooking_time[self.value()] == self.get_histogram(recipes):
            print(self.get_histogram(recipes))

        return recipes

    @staticmethod
    def filter_by_cooking_time_range(recipes, start, end):

        return recipes.filter(cooking_time__range=(start, end))


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return [
            ('has_recipes=0', 'Нет'),
            ('has_recipes=1', 'Да')
        ]

    def queryset(self, request, users):
        if self.value() == 'has_recipes=0':
            return users.annotate(
                has_recipes=Count('recipes')
            ).filter(recipes__isnull=True).filter(has_recipes=0)

        if self.value() == 'has_recipes=1':
            return users.annotate(
                has_recipes=Count('recipes')
            ).filter(recipes__isnull=False).filter(has_recipes__gte=1)


class HasFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return [
            ('has_followers=0', ('Нет')),
            ('has_followers=1', ('Да'))
        ]

    def queryset(self, request, users):
        if self.value() == 'has_followers=0':
            return users.annotate(
                has_followers=Count('followers')
            ).filter(followers__isnull=True).filter(has_followers=0)

        if self.value() == 'has_followers=1':
            return users.annotate(
                has_followers=Count('followers')
            ).filter(followers__isnull=False).filter(has_followers__gte=1)


class HasFollowingAuthorsFilter(admin.SimpleListFilter):
    title = ('Есть подписки')
    parameter_name = 'has_following_authors'

    def lookups(self, request, model_admin):
        return [
            ('has_following_authors=0', ('Нет')),
            ('has_following_authors=1', ('Да'))
        ]

    def queryset(self, request, users):
        if self.value() == 'has_following_authors=0':
            return users.annotate(
                has_following_authors=Count('authors')
            ).filter(authors__isnull=True).filter(has_following_authors=0)

        if self.value() == 'has_following_authors=1':
            return users.annotate(
                has_following_authors=Count('authors')
            ).filter(authors__isnull=False
                     ).filter(has_following_authors__gte=1)
