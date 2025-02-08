from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (permissions, pagination,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.filtersets import IngredientFilter, RecipeFilterSet
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (AuthorFollowRepresentSerializer,
                             IngredientSerializer,
                             RecipeAddUpdateSerializer,
                             RecipeGetSerializer, RecipeGetShortSerializer,
                             TagSerializer,
                             UserListSerializer,
                             UserAvatarSerializer)
from api.utils import render_shopping_cart
from recipes.models import (Ingredient, Favorite, Follow,
                            Recipe, ShoppingCart, Tag)


User = get_user_model()


class FoodgramPaginator(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class UsersViewSet(UserViewSet):
    """Вьюсет для работы с пользователями"""

    @action(methods=('get', 'patch'),
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    # Профиль пользователя
    def get_user_profile(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User,
                                     username=request.user.username)
            serializer = UserListSerializer(user,
                                            context={'request': request})
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
    # Смена аватарки
    def set_avatar(self, request):
        if request.method == 'PUT':
            if 'avatar' in request.data:
                print(request.data)
                serializer = UserAvatarSerializer(
                    request.user,
                    data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
            else:
                raise ValidationError('Загрузите аватар!')

        if request.method == 'DELETE':
            data = request.data
            if 'avatar' not in data:
                data = {'avatar': None}
            serializer = UserAvatarSerializer(request.user,
                                              data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(avatar=None)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get',),
            url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    # Подписки пользователя
    def get_subscriptions(self, request, **kwargs):
        paginator = FoodgramPaginator()
        subscription_authors = [
            subscription.author for subscription in
            Follow.objects.filter(user=request.user)
        ]
        paginated_subscriptions = paginator.paginate_queryset(
            subscription_authors, request
        )
        serializer = AuthorFollowRepresentSerializer(
            paginated_subscriptions,
            many=True,
            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(methods=('post', 'delete',),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Подписка на пользователя
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.pop('id'))

        if request.method == 'POST':
            if Follow.objects.filter(user=user,
                                     author=author).exists():
                raise ValidationError(
                    f'Вы уже подписаны на пользователя {author.username}'
                )

            if author == user:
                raise ValidationError('Вы не можете подписаться на себя!')
            Follow.objects.create(user=user, author=author)

            serializer = AuthorFollowRepresentSerializer(
                author,
                context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all()
    search_fields = ('author.id', 'tags', 'user.favorites')
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeAddUpdateSerializer
        return RecipeGetSerializer


    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление в избранное
    def favorite(self, request, *args, **kwargs):

        if request.method == 'POST':
            recipe = self.add_favorite_shopping_cart(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=kwargs['pk']),
                model=Favorite)

            return Response(RecipeGetShortSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            return self.delete_favorite_shopping_cart(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=kwargs['pk']),
                model=Favorite)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление рецепта в корзину
    def shopping_cart(self, request, *args, **kwargs):

        if request.method == 'POST':

            recipe = self.add_favorite_shopping_cart(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=kwargs['pk']),
                model=ShoppingCart)

            return Response(RecipeGetShortSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':

            return self.delete_favorite_shopping_cart(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=kwargs['pk']),
                model=ShoppingCart)

    @action(methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    # Скачивание ингредиентов для рецептов, добавленных в корзину
    def download_shopping_cart(self, request, *args, **kwargs):
        if request.user.shopping_cart.exists():
            return render_shopping_cart(self, request, *args, **kwargs)
        raise ValidationError('Отсутствуют рецепты в корзине')

    def add_favorite_shopping_cart(self, user, recipe, model):
        """Функция для добавления рецепта в избранное или в корзину"""

        if model.objects.filter(user=user,
                                recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен')

        return model.objects.create(user=user, recipe=recipe).recipe

    def delete_favorite_shopping_cart(self, user, recipe, model):
        """Функция для удаления рецепта из избранного или в корзины"""

        get_object_or_404(model,
                          user=user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения информации о тэгах"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения информации об ингредиентах"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
