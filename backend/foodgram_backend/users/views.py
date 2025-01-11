from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework import (filters, generics,
                            permissions,
                            status, viewsets)
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, UserGetTokenSerializer, FollowSerializer
from .models import Follow

User = get_user_model()


class UserGetToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = UserGetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user:
            token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
            return Response({
                'token': token.key
            })
        return Response('The user does not exist', status=status.HTTP_404_NOT_FOUND)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(methods=('get', 'patch'),
           url_path='me',
           permission_classes=(permissions.IsAuthenticated,),
           detail=False)
    def get_user_profile(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User,
                                     username=request.user.username)
            serializer = UserSerializer(user)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(methods=('get',),
            url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_subscriptions(self, request):
        subscriptions = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(subscriptions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('post', 'delete',),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def subscribe(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={
                    'user': request.user.id,
                    'following': get_object_or_404(User, id=kwargs['pk']).id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=request.user, following=kwargs['pk']).exists():
                return Response(
                    {'Error': 'You are not following this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(user=request.user,
                               following=get_object_or_404(User, id=kwargs['pk'])).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
