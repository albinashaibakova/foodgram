from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


User = get_user_model()

NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 32
TAG_MAX_LENGTH = 32
INGREDIENT_MAX_LENGTH = 128
MEASURE_MAX_LENGTH = 64
COOKING_TIME_MIN = 1


class Tag(models.Model):
    name = models.CharField(max_length=TAG_MAX_LENGTH,
                            unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            unique=True,
                            validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')],
                            verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_MAX_LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=MEASURE_MAX_LENGTH,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipes',
                                         verbose_name='Список ингредиентов')
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  through='TagRecipe',
                                  verbose_name='Список тегов')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.SmallIntegerField(
        validators=[MinValueValidator(COOKING_TIME_MIN)],
        verbose_name='Время приготовления (в минутах)'
    )
    image = models.BinaryField(verbose_name='Ссылка на картинку на сайте')
    is_favorited = models.BooleanField(verbose_name='Находится ли в избранном',
                                       default=False)
    is_in_shopping_cart = models.BooleanField(verbose_name='Находится ли в корзине',
                                              default=False)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe.name} содержит {self.tag.name}'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(validators=[MinValueValidator(1)],
                                 max_digits=5,
                                 decimal_places=2,
                                 verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe.name} содержит {self.ingredient}'


class Favourite(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favourites',
                               verbose_name='Рецепты в избранном')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favourites',
                             verbose_name='Автор рецепта')

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return f'{self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт в корзине')

    class Meta:
        verbose_name = 'Рецепты в корзине'

    def __str__(self):
        return f'{self.recipe.name}'
