from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (permissions, pagination,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.filtersets import IngredientFilter, RecipeFilterSet
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    AuthorFollowRepresentSerializer,
    IngredientSerializer, RecipeAddUpdateSerializer,
    RecipeGetSerializer, RecipeGetShortSerializer,
    TagSerializer, UserAvatarSerializer)
from api.utils import render_shopping_cart
from recipes.models import (
    Ingredient, Favorite, Follow, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)


User = get_user_model()


class FoodgramPaginator(pagination.PageNumberPagination):
    page_size_query_param = 'limit'


class UsersViewSet(UserViewSet):
    """Вьюсет для работы с пользователями"""

    @action(methods=('get', 'patch'),
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_user_profile(self, request):
        """Профиль пользователя"""
        return self.me(request)

    @action(methods=('put', 'delete'),
            url_path='me/avatar',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def set_avatar(self, request):
        """Смена аватарки"""
        if request.method == 'PUT':

            if 'avatar' not in request.data:
                raise ValidationError('Загрузите аватар!')

            serializer = UserAvatarSerializer(
                request.user,
                data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        os.remove('media/' + str(request.user.avatar))
        serializer = UserAvatarSerializer(
            request.user,
            data={'avatar': None}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get',),
            url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_subscriptions(self, request, **kwargs):
        """Подписки пользователя"""
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
    def subscribe(self, request, *args, **kwargs):
        """Подписка на пользователя"""
        user = request.user
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            if author == user:
                raise ValidationError('Вы не можете подписаться на себя!')
            try:
                Follow.objects.create(user=user, author=author)
                serializer = AuthorFollowRepresentSerializer(
                    author,
                    context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {
                        'error_message':
                            'Вы уже подписаны на пользователя!'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
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

    @action(methods=('get',),
            url_path='get-link',
            detail=True)
    def get_recipe_short_link(self, request, pk=None):
        self.get_object()
        url = reverse('short_link', kwargs={'pk': pk})
        original_url = request.build_absolute_uri(url)
        return HttpResponse(json.dumps({'short-link': original_url}),
                            content_type='application/json')

    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def favorite(self, request, *args, **kwargs):
        """Добавление в избранное"""
        if request.method == 'POST':
            return self.add_favorite_shopping_cart(request, model=Favorite)
        return self.delete_favorite_shopping_cart(request, model=Favorite)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление рецепта в корзину"""
        if request.method == 'POST':
            return self.add_favorite_shopping_cart(request, model=ShoppingCart)
        return self.delete_favorite_shopping_cart(request, model=ShoppingCart)

    @action(methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачивание ингредиентов для рецептов, добавленных в корзину"""
        recipes = request.user.shoppingcarts.values_list(
            'recipe__name',
            'recipe__author__username'
        )
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user).values(
                'recipe__name',
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
            quantity=Sum('amount')).order_by('amount')
        shopping_list, filename = render_shopping_cart(
            self,
            recipes,
            ingredients
        )
        return FileResponse(shopping_list,
                            filename=filename,
                            content_type='text/plain')

    def add_favorite_shopping_cart(self, request, model):
        """Функция для добавления рецепта в избранное или в корзину"""
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=request.parser_context['kwargs']['pk']
        )
        try:
            return Response(
                RecipeGetShortSerializer(
                    model.objects.create(
                        user=user,
                        recipe=recipe).recipe).data,
                status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'error_message': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete_favorite_shopping_cart(self, request, model):
        """Функция для удаления рецепта из избранного или в корзины"""
        user = request.user
        recipe = get_object_or_404(
            Recipe,
            id=request.parser_context['kwargs']['pk']
        )
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
