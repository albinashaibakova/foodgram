from rest_framework.reverse import reverse
from shortener.models import LinkShortener
from rest_framework import serializers

class ShortenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkShortener
        fields = '__all__'


    def to_representation(self, instance):
        return {'short-link': self.get_short_link(instance)}