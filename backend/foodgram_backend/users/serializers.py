from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Follow

User = get_user_model()


class UserGetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
