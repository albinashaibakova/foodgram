from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from recipes.models import (Ingredient, Favorite,
                            Follow,
                            RecipeIngredient,
                            Recipe, ShoppingCart,
                            Tag)
from recipes.admin_filters import (CookingTimeFilter,
                                   HasRecipesFilter,
                                   HasFollowersFilter,
                                   HasFollowingAuthorsFilter)

User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):

    model = RecipeIngredient
    min_num = 1


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'last_first_name',
                    'avatar',
                    'recipes_count',
                    'following_authors_count',
                    'followers_count')
    search_fields = ('username',
                     'email',)
    list_filter = [HasRecipesFilter, HasFollowersFilter, HasFollowingAuthorsFilter]
    list_per_page = 25

    def last_first_name(self, user):
        return ' '.join([user.last_name, user.first_name])

    @mark_safe
    def avatar(self, user):
        return '<img src="%s" width ="50" height="50"/>'%(user.avatar)

    def recipes_count(self, user):
        return user.recipes.count()

    def following_authors_count(self, user):
        return user.authors.count()

    def followers_count(self, user):
        return user.followers.count()

    last_first_name.short_description = 'Фамилия Имя'
    recipes_count.short_description = 'Количество рецептов'
    following_authors_count.short_description = 'Количество подписок'
    followers_count.short_description = 'Количество подписчиков'


class RecipesCountMixin(admin.ModelAdmin):
    list_display = ('recipes_count', )

    def recipes_count(self, obj):
        return obj.recipes.count()

    recipes_count.short_description = 'Количество рецептов'


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
    list_display = ('id',
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

    def is_favorite_count(self, recipe):
        return recipe.favorites.count()

    @mark_safe
    def recipe_image(self, recipe):
        return '<img src="%s" width ="50" height="50"/>'%(recipe.image)

    @mark_safe
    @admin.display(description='Продукты')
    def display_ingredients(self, recipe):
        ingredients_info = []

        for recipeingredient in recipe.recipeingredients.all():
            ingredients_info.append(
                f'{recipeingredient.ingredient.name.capitalize()} - '
                f'{recipe.recipeingredients.get(ingredient=recipeingredient.ingredient.id).amount} '
                f'{recipeingredient.ingredient.measurement_unit}<br>'
            )

        return ''.join(ingredients_info)

    @mark_safe
    @admin.display(description='Тэги', )
    def display_tags(self, recipe):
        tags_info = []
        for tag in recipe.tags.all():
            tags_info.append(
                f'{tag.name}<br>'
            )
        return ''.join(tags_info)

    is_favorite_count.short_description = 'Сколько раз в избранном'
    recipe_image.short_description = 'Картинка блюда'

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


@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_per_page = 25


@admin.register(ShoppingCart)
class ShoppingCart(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_per_page = 25


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_per_page = 25
