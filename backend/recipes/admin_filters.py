from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

class HasRecipesFilter(admin.SimpleListFilter):
    title = _('Есть рецепты')
    parameter_name = 'Есть рецепты'

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
    parameter_name = 'Есть подписчики'

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
    parameter_name = 'Есть подписки'

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