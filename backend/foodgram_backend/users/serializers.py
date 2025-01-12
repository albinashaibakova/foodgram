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


#class UserViewSetSerializer(UserSerializer):

 #   class Meta:
 #       model = User
 #       fields = ('email', 'id', 'username', 'first_name',
 #                 'last_name')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
