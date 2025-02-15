import numpy
from django.contrib import admin
from django.db.models import Count, Avg
import numpy as np


class CookingTimeFilter(admin.SimpleListFilter):

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def get_average_cooking_time(self, recipes):
        recipes_count = recipes.all().count()
        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        if min(cooking_time) == max(cooking_time):
            return recipes

        average_cooking_time = recipes.all().aggregate(Avg('cooking_time'))['cooking_time__avg']

        cooking_time = [recipe.cooking_time for recipe in recipes.all()]

        bins = [min(cooking_time),  round(average_cooking_time), max(cooking_time)]

        hists, bins = np.histogram(cooking_time, bins=bins)

        return bins[0], bins[-1]

    def lookups(self, request, model_admin):

        recipes = model_admin.get_queryset(request)
        if recipes:
            less_avg, more_avg = self.get_average_cooking_time(recipes)

            return [
                ('less_than_avg', (
                    f'Меньше {less_avg} минут '
                    f'('
                    f'{recipes.filter(cooking_time__lte=less_avg).count()}'
                    f')')),

                ('avg', (
                    f'Меньше {more_avg} минут '
                    f'('
                    f'''{recipes.filter(cooking_time__lt=more_avg,
                                        cooking_time__gt=less_avg).count()}'''
                    f')')),

                ('more_than_avg', (
                    f'Дольше {more_avg} минут '
                    f'({recipes.filter(cooking_time__gte=more_avg).count()})'))
            ]

    def queryset(self, request, recipes):
        if recipes:
            less_avg, more_avg = self.get_average_cooking_time(recipes)

            if self.value() == 'less_than_avg':
                return recipes.filter(cooking_time__lte=less_avg)

            if self.value() == 'avg':
                return recipes.filter(cooking_time__lt=more_avg,
                                      cooking_time__gt=less_avg)

            if self.value() == 'more_than_avg':
                return recipes.filter(cooking_time__gte=more_avg)


class HasRecipesFilter(admin.SimpleListFilter):
    title = ('Есть рецепты')
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return [
            ('has_recipes=0', ('Нет')),
            ('has_recipes=1', ('Да'))
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
    title = ('Есть подписчики')
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
