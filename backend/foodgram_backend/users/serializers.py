from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers

from .models import Follow

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

    class Meta:
        model = User
        fields = ('avatar', )

    def validate_avatar(self, value):
        if type(value) is str:
            return value.encode('ascii')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
