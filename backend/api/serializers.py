import string
from random import choice

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializer_fields import Base64ImageField
from recipes.models import (Ingredient, RecipeIngredient,
                            Favorite, Follow, Recipe,
                            ShoppingCart, Tag)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSignUpSerializer(UserCreateSerializer):
    avatar = Base64ImageField(default='media/users/default-avatar.jpg',
                              read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'avatar')


class UserListSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (user.is_authenticated
                and author != user
                and Follow.objects.filter(user=user,
                                          author=author).exists())


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar', )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами в рецепте"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов,
     входящих в состав рецепта"""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте"""

    ingredients = IngredientGetSerializer(many=True,
                                          read_only=True,
                                          source='recipe_ingredients')
    author = UserListSerializer()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user,
                    recipe=recipe.id).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = (self.context.get('request'))
        return (request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=recipe.id).exists())


class RecipeAddUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения рецепта"""

    ingredients = AddIngredientSerializer(
        many=True, write_only=True,
        source='recipe_ingredients'
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    slug = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'slug'
        )


    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return Favorite.objects.filter(user=user,
                                       recipe=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user,
                                       recipe=recipe.id).exists()

    def get_slug(self, instance):
        if self.context['request'].method == 'POST':
            slug = ''.join(choice(string.ascii_letters)
                           for x in range(10))

            return slug
        return instance.slug

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствуют ингредиенты!'
            )
        ingredient_list = []
        for recipe_ingredient in ingredients:

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

        RecipeIngredient.objects.bulk_create(RecipeIngredient(
            ingredient=recipe_ingredient['ingredient'],
            recipe=recipe,
            amount=recipe_ingredient['amount']
        )
        for recipe_ingredient in ingredients)

        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients_tags(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.add_ingredients_tags(instance, ingredients, tags)
        instance.save()
        return super().update(instance, validated_data)

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
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class AuthorFollowRepresentSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о подписках пользователя"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, author):
        recipes_limit = int(self.context['request'].GET.get('recipes_limit', 10 ** 10))
        recipes = Recipe.objects.filter(author=author)
        return RecipeGetShortSerializer(
            recipes[:recipes_limit], many=True).data

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (user.is_authenticated
                and author != user
                and Follow.objects.filter(user=user,
                                          author=author).exists())
