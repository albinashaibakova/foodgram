import string
from random import random, choice

from rest_framework.reverse import reverse
from shortener.models import LinkShortener
from rest_framework import serializers

class ShortenerSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()

    class Meta:
        model = LinkShortener
        fields = ('long_url', 'slug')

    def to_representation(self, instance):
        print(instance.__dict__)
        slug = instance.slug
        return {'short-link': slug}