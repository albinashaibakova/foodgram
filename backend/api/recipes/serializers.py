from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializer_fields import Base64ImageField
from api.users.serializers import UserListSerializer
from recipes.models import (Ingredient, IngredientRecipe,
                            Favorite, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow


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
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetSerializer(many=True,
                                          read_only=True,
                                          source='recipe_ingredients')
    author = UserListSerializer()

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if (request.user.is_authenticated
                and Favorite.objects.filter(user=request.user,
                                            recipe=obj.id).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (request.user.is_authenticated
                and ShoppingCart.objects.filter(user=request.user,
                                                recipe=obj.id).exists()):
            return True
        return False


class RecipeAddUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
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
            raise serializers.ValidationError(
                'Отсутствуют ингредиенты!'
            )
        ingredient_list = []
        for recipe_ingredient in ingredients:
            if not Ingredient.objects.filter(
                    id=recipe_ingredient['id']).exists():
                raise serializers.ValidationError(
                    'Ингредиент не присутствует в списке'
                )
            if recipe_ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть равно нулю'
                )
            recipe_ingredient = get_object_or_404(
                Ingredient,
                id=recipe_ingredient['id']
            )
            if recipe_ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты повторяются'
                )
            ingredient_list.append(recipe_ingredient)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Отсутствуют тэги!'
            )
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Тэги повторяются'
                )
            tag_list.append(tag)
        return tags

    @staticmethod
    def add_ingredients_tags(recipe, ingredients, tags):
        recipe.tags.set(tags)
        for recipe_ingredient in ingredients:
            ingredient = Ingredient.objects.get(
                id=recipe_ingredient['id']
            )
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=recipe_ingredient['amount'])
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_ingredients_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.add_ingredients_tags(instance, ingredients, tags)
        instance.save()
        return instance

    def validate(self, attrs):
        if not attrs.get('image'):
            raise serializers.ValidationError(
                'Рецепт должен содержать изображение')
        if not attrs.get('recipe_ingredients'):
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты')
        if not attrs.get('tags'):
            raise serializers.ValidationError(
                'Рецепт должен содержать тэги'
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe',)

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = RecipeShortSerializer(recipe)
        return serializer.data


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class FollowSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        self.recipes_limit = kwargs.pop('recipes_limit', None)
        super(FollowSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Follow
        fields = '__all__'

    def to_representation(self, instance, **kwargs):
        recipes_limit = self.recipes_limit
        kwargs['recipes_limit'] = recipes_limit
        serializer = FollowGetSerializer(instance, **kwargs)
        return serializer.data

    def validate(self, data):
        if self.context['request'].user.id == data['following'].id:
            raise ValidationError('Вы не можете подписаться на себя!')
        return data


class FollowGetSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    email = serializers.ReadOnlyField(source='following.email')
    is_subscribed = serializers.ReadOnlyField(source='following.is_subscribed')
    avatar = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def __init__(self, *args, **kwargs):
        self.recipes_limit = kwargs.pop('recipes_limit', None)
        super(FollowGetSerializer, self).__init__(*args, **kwargs)

    def get_avatar(self, obj):
        if obj.following.avatar:
            return obj.following.avatar
        else:
            return None

    def get_recipes(self, obj):
        if self.recipes_limit:
            recipes_limit = int(self.recipes_limit)
            recipes = Recipe.objects.filter(author=obj.following)[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(author=obj.following)
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
