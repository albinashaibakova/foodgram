from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import (Ingredient, RecipeIngredient,
                            Recipe, Tag,)


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')


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

