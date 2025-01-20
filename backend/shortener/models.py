from django.db import models

URL_MAX_LENGTH = 200


class LinkShortener(models.Model):
    """Модель для хранения коротких ссылок на рецепт"""

    long_url = models.CharField(max_length=URL_MAX_LENGTH, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Короткая ссылка на рецепт'
        verbose_name_plural = 'Короткие ссылки на рецепт'
        unique_together = (('long_url', 'slug'),)
