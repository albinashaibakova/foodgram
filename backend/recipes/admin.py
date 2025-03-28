from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from recipes.models import (
    Ingredient, Favorite,
    Follow,
    RecipeIngredient,
    Recipe, ShoppingCart, Tag
)
from recipes.admin_filters import (
    CookingTimeFilter,
    IsInRecipesFilter,
    HasFollowersFilter,
    HasFollowingAuthorsFilter,
    HasRecipesFilter
)

User = get_user_model()

admin.site.unregister(Group)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipesCountMixin:
    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        if isinstance(obj, Ingredient):
            return obj.recipeingredients.count()
        return obj.recipes.count()


@admin.register(User)
class FoodgramUserAdmin(RecipesCountMixin, UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'last_first_name',
        'user_avatar',
        'recipes_count',
        'following_authors_count',
        'followers_count'
    )
    search_fields = ('username', 'email')
    list_filter = [
        HasRecipesFilter,
        HasFollowersFilter,
        HasFollowingAuthorsFilter]
    list_per_page = 25

    @admin.display(description='Фамилия Имя')
    def last_first_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def user_avatar(self, user):
        if not user.avatar:
            return None
        return f'<img src={user.avatar.url} width ="50" height="50"/>'

    @admin.display(description='Подписки')
    def following_authors_count(self, user):
        return user.subscriptions.count()

    @admin.display(description='Подписчики')
    def followers_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Рецепты')
    @mark_safe
    def recipes_list(self, user):
        return '<br>'.join(recipe.name for recipe in user.recipes.all())

    @admin.display(description='Подписки')
    @mark_safe
    def following_authors_list(self, user):
        return '<br>'.join(
            follow.author.username for follow in user.subscriptions.all()
        ) if user.subscriptions.all() else 'Нет подписок'

    @admin.display(description='Подписчики')
    @mark_safe
    def followers_list(self, user):
        return '<br>'.join(
            follow.user.username for follow in user.subscribers.all()
        ) if user.subscribers.all() else 'Нет подписчиков'

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'username',
                    'email',
                    'password',
                    ('first_name', 'last_name'),
                    'avatar',
                )
            },
        ),
        ('Рецепты',
         {
             'fields': (
                 'recipes_list',
             ),
             'classes': ('collapse',),
         }
         ),
        ('Подписки',
         {
             'fields': (
                 'following_authors_list',
             ),
             'classes': ('collapse',),
         }
         ),
        ('Подписчики',
         {
             'fields': (
                 'followers_list',
             ),
             'classes': ('collapse',),
         }
         )
    )

    readonly_fields = (
        'recipes_list',
        'following_authors_list',
        'followers_list'
    )


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', IsInRecipesFilter)
    list_per_page = 25


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')
    list_per_page = 25


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'short_cooking_time',
        'author',
        'display_tags',
        'is_favorite_count',
        'display_ingredients',
        'recipe_image')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('tags', 'author', CookingTimeFilter)
    list_per_page = 25
    inlines = [RecipeIngredientInline]

    @admin.display(description='Время (мин)')
    def short_cooking_time(self, recipe):
        return recipe.cooking_time

    @admin.display(description='В избранном')
    def is_favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Изображение')
    @mark_safe
    def recipe_image(self, recipe):
        if not recipe.image:
            return None
        return f'<img src={recipe.image.url} width ="50" height="50"/>'

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        return '<br>'.join(
            '{name} - {amount}' '{measurement_unit}'.format(
                name=recipeingredient.ingredient.name.capitalize(),
                amount=recipeingredient.amount,
                measurement_unit=recipeingredient.ingredient.measurement_unit
            ) for recipeingredient in recipe.recipeingredients.all()
        )

    @mark_safe
    @admin.display(description='Тэги', )
    def display_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time',),
                    'text',
                    'image',
                    'tags',
                )
            },
        ),
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount')
    list_filter = ('ingredient',)
    search_fields = ('recipe',)
    list_per_page = 25


@admin.register(Favorite, ShoppingCart)
class Favorite(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_per_page = 25


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_per_page = 25
