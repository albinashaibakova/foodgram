from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import (permissions, pagination,
                            status, viewsets)
from rest_framework.response import Response

from api.serializers import FollowSerializer
from .serializers import UserListSerializer, UserAvatarSerializer
from .models import Follow

User = get_user_model()



class FoodgramPaginator(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class UsersViewSet(UserViewSet):


    @action(methods=('get', 'patch'),
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_user_profile(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User,
                                     username=request.user.username)
            serializer = UserListSerializer(user)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        serializer = UserListSerializer(request.user,
                                        data=request.data,
                                        partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(methods=('put', 'delete'),
            url_path='me/avatar',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def set_avatar(self, request):
        if request.method == 'PUT':
            if 'avatar' in request.data:
                serializer = UserAvatarSerializer(request.user,
                                                  data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(avatar=serializer.validate_avatar(request.data['avatar']))
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            serializer = UserAvatarSerializer(request.user,
                                              data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(avatar=None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(methods=('get',),
            url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_subscriptions(self, request, **kwargs):
        recipes_limit = request.query_params.get('recipes_limit')
        kwargs['recipes_limit'] = recipes_limit
        subscriptions = Follow.objects.filter(user=request.user)
        paginator = FoodgramPaginator()
        paginated_subscriptions = paginator.paginate_queryset(subscriptions, request)
        serializer = FollowSerializer(paginated_subscriptions, many=True, **kwargs)
        return paginator.get_paginated_response(serializer.data)


    @action(methods=('post', 'delete',),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        following = get_object_or_404(User, id=kwargs.pop('id'))
        recipes_limit = request.query_params.get('recipes_limit')
        kwargs['recipes_limit'] = recipes_limit

        if request.method == 'POST':
            serializer = FollowSerializer(
            data={'user': user.id, 'following': following.id},
            context={'request': request}, **kwargs
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user,
                                         following=following).exists():
                return Response(
                    {'Error': 'You are not following this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(user=user,
                               following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
