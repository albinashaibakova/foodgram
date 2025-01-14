import string
from random import choice, randint

from django.db import models

class LinkShortener(models.Model):

    long_url = models.CharField(max_length=200)
    short_url = models.CharField(max_length=15)

    class Meta:
        abstract = True
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        unique_together = (('long_url', 'short_url'),)


