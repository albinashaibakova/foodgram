from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


USERNAME_MAX_LENGTH = 150
FIST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 256
MAX_STR_VALUE_LENGTH = 10
ROLE_MAX_LENGTH = 15
PASSWORD_MAX_LENGTH = 60


class FoodgramUser(AbstractUser):
    """Модель пользователя сервиса FOODGRAM"""

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (ADMIN, ADMIN),
        (USER, USER)
    )

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Уникальный юзернейм',
        validators=[RegexValidator(regex=r'^[\w.@+-]+$')]
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты')
    password = models.CharField(
        max_length=PASSWORD_MAX_LENGTH,
        verbose_name='Пароль'
    )
    first_name = models.CharField(
        max_length=FIST_NAME_MAX_LENGTH,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        verbose_name='Фамилия')
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписан ли текущий пользователь на этого'
    )
    avatar = models.BinaryField(
        blank=True,
        null=True,
        verbose_name='Ссылка на аватар')
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль пользователя')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    def __str__(self):
        return self.username[:MAX_STR_VALUE_LENGTH]

    @property
    def is_admin(self):
        return (self.role == self.ADMIN
                or self.is_superuser)


class Follow(models.Model):
    """Модель для описания подписки на пользователя"""

    user = models.ForeignKey(FoodgramUser,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    following = models.ForeignKey(FoodgramUser,
                                  on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='Автор рецепта')

    class Meta:
        verbose_name = 'Подписки пользователя'
        unique_together = ('user', 'following')

    def __str__(self):
        return f'{self.user} подписан на автора {self.following}'
