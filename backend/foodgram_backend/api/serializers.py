from rest_framework import serializers
from recipes.models import Ingredient, Favourite, Recipe, Tag, ShoppingCart


class RecipeGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeAddUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'

    def perform_create(self, serializer):
        serializer.save()
        return serializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'
