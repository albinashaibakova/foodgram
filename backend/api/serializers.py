from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api.serializer_fields import (
    Base64ImageField,
    GetIsFavoritedShippingCartField
)
from recipes.models import (
    Ingredient, Favorite, Follow,
    RecipeIngredient, Recipe,
    ShoppingCart, Tag
)
from recipes.models import MIN_AMOUNT, NAME_MAX_LENGTH

User = get_user_model()


class UserRepresentSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = tuple(UserSerializer.Meta.fields) + ('avatar', 'is_subscribed')

    def get_is_subscribed(self, author):

        user = self.context.get('request').user
        return (user.is_authenticated
                and author != user
                and Follow.objects.filter(
                    user=user,
                    author=author
                ).exists())


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
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

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
        read_only_fields = fields


class RecipeGetShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте"""

    ingredients = IngredientGetSerializer(
        many=True,
        read_only=True,
        source='recipeingredients')
    author = UserRepresentSerializer()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = GetIsFavoritedShippingCartField(model=Favorite)
    is_in_shopping_cart = GetIsFavoritedShippingCartField(model=ShoppingCart)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeAddUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения рецепта"""

    ingredients = AddIngredientSerializer(
        many=True, write_only=True,
        source='recipeingredients'
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    name = serializers.CharField(max_length=NAME_MAX_LENGTH)
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

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
            'cooking_time'
        )

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

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=recipe_ingredient['ingredient'],
                recipe=recipe,
                amount=recipe_ingredient['amount'])
            for recipe_ingredient in ingredients)

        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        serializer = RecipeGetShortSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients_tags(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.recipeingredients.all().delete()
        self.add_ingredients_tags(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def validate(self, attrs):
        if not attrs.get('image'):
            raise serializers.ValidationError(
                'Рецепт должен содержать изображение')
        if not attrs.get('recipeingredients'):
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


class AuthorFollowRepresentSerializer(UserRepresentSerializer):
    """Сериализатор для отображения информации о подписках пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserRepresentSerializer.Meta):
        model = User
        fields = (
                tuple(UserRepresentSerializer.Meta.fields) +
                ('recipes', 'recipes_count',)
        )

    def get_recipes(self, author):

        return RecipeGetShortSerializer(
            Recipe.objects.filter(author=author)[:int(
                self.context['request'].GET.get('recipes_limit', 10 ** 10)
            )], many=True).data
