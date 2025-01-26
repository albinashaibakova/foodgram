from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


USERNAME_MAX_LENGTH = 150
FIST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 256
MAX_STR_VALUE_LENGTH = 10
ROLE_MAX_LENGTH = 15
PASSWORD_MAX_LENGTH = 200

NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 32
TAG_MAX_LENGTH = 32
INGREDIENT_MAX_LENGTH = 128
MEASURE_MAX_LENGTH = 20
COOKING_TIME_MIN = 1
MAX_REPR_LENGTH_TAG_INGREDIENT = 10
MAX_REPR_LENGTH_RECIPE = 20


class FoodgramUser(AbstractUser):
    """Модель пользователя сервиса FOODGRAM"""

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Юзернейм',
        validators=[RegexValidator(regex=r'^[\w.@+-]+$')]
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты')
    first_name = models.CharField(
        max_length=FIST_NAME_MAX_LENGTH,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        verbose_name='Фамилия')
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='users/avatars/',
        verbose_name='Ссылка на аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password',
                       'first_name', 'last_name']

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Пользователь Foodgram'
        verbose_name_plural = 'Пользователи Foodgram'

    def __str__(self):
        return self.username[:MAX_STR_VALUE_LENGTH]


class Follow(models.Model):
    """Модель для описания подписки на пользователя"""

    user = models.ForeignKey(FoodgramUser,
                             on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='Пользователь')
    author = models.ForeignKey(FoodgramUser,
                               on_delete=models.CASCADE,
                               related_name='authors',
                               verbose_name='Автор рецепта')

    class Meta:
        verbose_name = 'Подписчик автора рецепта'
        verbose_name_plural = 'Подписчики автора рецепта'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} подписан на автора {self.author}'


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

    author = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE,
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
    image = models.ImageField(verbose_name='Ссылка на картинку на сайте',
                              upload_to='recipes/images',
                              null=False)
    is_favorited = models.BooleanField(verbose_name='Находится ли в избранном',
                                       default=False)
    is_in_shopping_cart = models.BooleanField(
        verbose_name='Находится ли в корзине',
        default=False)

    class Meta:
        ordering = ('-id',)
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
    user = models.ForeignKey(FoodgramUser,
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
