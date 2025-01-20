import string
from random import choice

from rest_framework import serializers

from shortener.models import LinkShortener


class ShortenerSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    class Meta:
        model = LinkShortener
        fields = ('long_url', 'slug')

    def create(self, validated_data):
        print(validated_data)
        slug = self.get_slug()
        shortener = LinkShortener(long_url=validated_data['long_url'], slug=slug)
        shortener.save()
        return shortener

    def get_slug(self):
        slug = ''.join(choice(string.ascii_letters)
                           for x in range(10))
        return slug
