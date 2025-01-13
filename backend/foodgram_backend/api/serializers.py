from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import Ingredient, Favourite, Recipe, Tag, ShoppingCart, IngredientRecipe, TagRecipe
from rest_framework.exceptions import ValidationError

from users.serializers import UserListSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='recipe_ingredients')
    author = UserListSerializer()

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)


    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


class RecipeAddUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    author = UserListSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'


    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингредиенты!')
        ingredient_list = []
        for recipe_ingredient in ingredients:
            ingredient = get_object_or_404(Ingredient, id=recipe_ingredient['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингредиенты повторяются')
            ingredient_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Отсутствуют тэги!')
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError('Тэги повторяются')
            tag_list.append(tag)
        return tags

    def add_ingredients_tags(self, recipe, ingredients, tags):
        recipe.tags.set(tags)
        for recipe_ingredient in ingredients:
            ingredient = get_object_or_404(Ingredient, id=recipe_ingredient['id'])
            amount = recipe_ingredient['amount']
            IngredientRecipe.objects.update_or_create(ingredient=ingredient,
                                            recipe=recipe,
                                            amount=amount)
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        return self.add_ingredients_tags(recipe, ingredients, tags)

    def update(self, instance, validated_data):
        ingredients = validated_data['recipe_ingredients']
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        return self.add_ingredients_tags(recipe, ingredients, tags)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'
