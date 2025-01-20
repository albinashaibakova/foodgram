from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 32
TAG_MAX_LENGTH = 32
INGREDIENT_MAX_LENGTH = 128
MEASURE_MAX_LENGTH = 20
COOKING_TIME_MIN = 1
MAX_REPR_LENGTH_TAG_INGREDIENT = 10
MAX_REPR_LENGTH_RECIPE = 20
TEXT_MAX_LENGTH = 10000


class Tag(models.Model):
    """Модель для описания тэгов"""

    name = models.CharField(max_length=TAG_MAX_LENGTH,
                            unique=True,
                            verbose_name='Название')
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            unique=True,
                            verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_TAG_INGREDIENT]


class Ingredient(models.Model):
    """ Модель для описания ингредиентов"""

    name = models.CharField(max_length=INGREDIENT_MAX_LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=MEASURE_MAX_LENGTH,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_TAG_INGREDIENT]


class Recipe(models.Model):
    """Модель для описания рецепта"""

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
    text = models.TextField(max_length=TEXT_MAX_LENGTH,
                            verbose_name='Описание')
    cooking_time = models.SmallIntegerField(
        validators=[MinValueValidator(COOKING_TIME_MIN)],
        verbose_name='Время приготовления (в минутах)'
    )
    image = models.ImageField(verbose_name='Ссылка на картинку на сайте',
                              upload_to='recipes/images',
                              null=False)
    is_favorited = models.BooleanField(verbose_name='Находится ли в избранном',
                                       default=False)
    is_in_shopping_cart = models.BooleanField(
        verbose_name='Находится ли в корзине',
        default=False)

    class Meta:
        default_related_name = 'recipe'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_RECIPE]


class TagRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe.name} содержит {self.tag.name}'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients',)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    def __str__(self):
        return f'{self.recipe.name} содержит {self.ingredient}'


class FavoriteShoppingCartBaseModel(models.Model):
    """Общая модель рецепта в избранном и рецепта в корзине"""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Автор рецепта')

    class Meta:
        abstract = True
        unique_together = (('user', 'recipe'),)

    def __str__(self):
        return f'{self.recipe.name}'


class Favorite(FavoriteShoppingCartBaseModel):
    """Модель для описания добавления рецепта в избранное"""

    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'favorites'


class ShoppingCart(FavoriteShoppingCartBaseModel):
    """Модель для описания добавления рецепта в корзину"""

    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        default_related_name = 'shopping_cart'
