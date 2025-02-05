from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _
import numpy as np



class CookingTimeFilter(admin.SimpleListFilter):
    title = _('Время приготовления')
    parameter_name = 'cooking_time'


    def get_average_cooking_time(self, recipes):
        recipes_count = recipes.all().count()
        average_cooking_time = recipes.all().aggregate(
            Sum('cooking_time')
        )['cooking_time__sum']

        std_deviation = np.std(recipes.all()['cooking_time'])

        return average_cooking_time, std_deviation


    def lookups(self, request, model_admin):

        return [
            ('less_than_average', _('Меньше 5 минут')),
            ('average', _('Меньше 20 минут')),
            ('more_than_average', _('Долго'))
        ]

    def queryset(self, request, recipes):
        print(self.get_average_cooking_time(recipes))
        if self.value() == 'less_than_average':
            return recipes.filter(cooking_time__lt=5)

        if self.value() == 'average':
            return recipes.filter(cooking_time__lt=20, cooking_time__gte=5)

        if self.value() == 'more_than_average':
            return recipes.filter(cooking_time__gte=20)


class HasRecipesFilter(admin.SimpleListFilter):
    title = _('Есть рецепты')
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return [
            ('has_recipes=0', _('Нет')),
            ('has_recipes=1', _('Да'))
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
    title = _('Есть подписчики')
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return [
            ('has_followers=0', _('Нет')),
            ('has_followers=1', _('Да'))
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
    title = _('Есть подписки')
    parameter_name = 'has_following_authors'

    def lookups(self, request, model_admin):
        return [
            ('has_following_authors=0', _('Нет')),
            ('has_following_authors=1', _('Да'))
        ]

    def queryset(self, request, users):
        if self.value() == 'has_following_authors=0':
            return users.annotate(
                has_following_authors=Count('authors')
            ).filter(authors__isnull=True).filter(has_following_authors=0)

        if self.value() == 'has_following_authors=1':
            return users.annotate(
                has_following_authors=Count('authors')
            ).filter(authors__isnull=False).filter(has_following_authors__gte=1)
