from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from recipes.models import (Ingredient, RecipeIngredient,
                            Recipe, Tag,)
from recipes.admin_filters import (HasRecipesFilter,
                                   HasFollowersFilter,
                                   HasFollowingAuthorsFilter)

User = get_user_model()



@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = ('username',
                    'email',
                    'last_first_name',
                    'password',
                    'recipes_count',
                    'following_authors_count',
                    'followers_count')
    search_fields = ('username',
                     'email',)
    list_filter = [HasRecipesFilter, HasFollowersFilter, HasFollowingAuthorsFilter]


    def last_first_name(self, user):
        return ' '.join([user.last_name, user.first_name])

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





@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('tags',)

    @admin.display(
        description='Список ингредиентов',
    )
    def display_ingredients(self, recipe):
        return ', '.join([ingredient.name
                          for ingredient in recipe.ingredients.all()])

    @admin.display(
        description='Список тэгов'
    )
    def display_tags(self, recipe):
        return ', '.join([tag.name for tag in recipe.tags.all()])


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient_id',
        'recipe_id'
    )
    list_filter = ('ingredient_id',)
    search_fields = ('recipe_id',)

