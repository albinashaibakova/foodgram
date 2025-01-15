import string
from random import choice, randint

from django.db import models

class LinkShortener(models.Model):

    long_url = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Короткая ссылка на рецепт'
        verbose_name_plural = 'Короткие ссылки на рецепт'
        unique_together = (('long_url', 'slug'),)
