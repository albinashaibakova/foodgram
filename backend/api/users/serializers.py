from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers

from api.custom_serializer_field import Base64ImageField


User = get_user_model()


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class UserListSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed', 'avatar')


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar', )
