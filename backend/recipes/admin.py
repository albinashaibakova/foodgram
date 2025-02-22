from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
    HasFollowersFilter,
    HasFollowingAuthorsFilter,
    HasRecipesFilter
)

User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):

    model = RecipeIngredient
    min_num = 1


class RecipesCountMixin:

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
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
        if user.avatar:
            return '<img src={avatar} width ="50" height="50"/>'.format(
                avatar=user.avatar.url
            )
        return '-'

    @admin.display(description='Количество подписок')
    def following_authors_count(self, user):
        return user.authors.count()

    @admin.display(description='Количество подписчиков')
    def followers_count(self, user):
        return user.followers.count()


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name',)
    list_filter = ('measurement_unit', )
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
        'cooking_time',
        'author',
        'display_tags',
        'is_favorite_count',
        'display_ingredients',
        'recipe_image')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('tags', 'author', CookingTimeFilter)
    list_per_page = 25
    inlines = [RecipeIngredientInline]

    @admin.display(description='Сколько раз в избранном')
    def is_favorite_count(self, recipe):
        return recipe.recipes_favorite.count()

    @admin.display(description='Изображение блюда')
    @mark_safe
    def recipe_image(self, recipe):
        return '<img src={image} width ="50" height="50"/>'.format(
            image=recipe.image.url
        )

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):

        return '<br>'.join(
            ['{ingredient_name} - {ingredient_amount} {ingredient_measurement_unit}'.format(
                ingredient_name=recipeingredient.ingredient.name.capitalize(),
                ingredient_amount=recipeingredient.amount,
                ingredient_measurement_unit=recipeingredient.ingredient.measurement_unit
            ) for recipeingredient in recipe.recipeingredients.all()]
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
        'amount'
    )
    list_filter = ('ingredient',)
    search_fields = ('recipe',)
    list_per_page = 25


@admin.register(Favorite, ShoppingCart)
class Favorite(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_per_page = 25


class ShoppingCart(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_per_page = 25


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_per_page = 25
