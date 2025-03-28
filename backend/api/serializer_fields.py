import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class GetIsFavoritedShippingCartField(serializers.BooleanField):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def get_attribute(self, instance):
        return instance

    def to_representation(self, recipe):
        return (self.context.get('request').user.is_authenticated
                and self.model.objects.filter(
                    user=self.context.get('request').user,
                    recipe=recipe.id).exists()
                )


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, data = data.split(';base64,')
            ext = header.split('/')[-1]
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                raise serializers.ValidationError(
                    'Картинка не валидна'
                )
            data = ContentFile(decoded_file, name=f'image.{ext}')
        return super().to_internal_value(data)
