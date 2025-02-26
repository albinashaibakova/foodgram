from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

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
MEASURE_MAX_LENGTH = 64
COOKING_TIME_MIN = 1
MAX_REPR_LENGTH_TAG_INGREDIENT = 10
MAX_REPR_LENGTH_RECIPE = 20
MIN_AMOUNT = 1


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
        verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email', )
        verbose_name = 'Пользователь Foodgram'
        verbose_name_plural = 'Пользователи Foodgram'

    def __str__(self):
        return self.username[:MAX_STR_VALUE_LENGTH]


class Follow(models.Model):
    """Модель для описания подписки на пользователя"""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчики')
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Авторы')

    class Meta:
        ordering = ('user__username', 'author__username',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} подписан на автора {self.author}'


class Tag(models.Model):
    """Модель для описания тэгов"""
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название')
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        ordering = ('slug',)
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_TAG_INGREDIENT]


class Ingredient(models.Model):
    """ Модель для описания продуктов"""
    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH,
        verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=MEASURE_MAX_LENGTH,
        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        constraints = [UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit')
        ]

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_TAG_INGREDIENT]


class Recipe(models.Model):
    """Модель для описания рецепта"""
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор')
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Продукты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.SmallIntegerField(
        validators=[MinValueValidator(COOKING_TIME_MIN)],
        verbose_name='Время приготовления (в минутах)'
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/images',
        null=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания рецепта'
    )

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:MAX_REPR_LENGTH_RECIPE]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт для рецепта')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Мера'
    )

    def __str__(self):
        return f'{self.recipe.name} содержит {self.ingredient}'

    class Meta:
        ordering = ('recipe__name', 'ingredient__name')
        verbose_name = 'Продукт для рецепта'
        verbose_name_plural = 'Продукты для рецептов'
        default_related_name = 'recipeingredients'


class RecipeUserBaseModel(models.Model):
    """Общая модель рецепта в избранном и рецепта в корзине"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь Foodgram')

    class Meta:
        abstract = True
        ordering = ('recipe__name', 'user__username')
        verbose_name = 'Рецепт в корзине/избранном'
        verbose_name_plural = 'Рецепты в корзине/избранном'
        default_related_name = '%(class)ss'
        constraints = [UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_user_%(class)s')]

    def __str__(self):
        return (f'Рецепт {self.recipe.name} добавлен '
                f'пользователем {self.user.username}')


class Favorite(RecipeUserBaseModel):
    """Модель для описания добавления рецепта в избранное"""
    class Meta(RecipeUserBaseModel.Meta):
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'


class ShoppingCart(RecipeUserBaseModel):
    """Модель для описания добавления рецепта в корзину"""
    class Meta(RecipeUserBaseModel.Meta):
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
