import aspose.pdf as ap
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
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
from api.serializers import (IngredientSerializer,
                             FollowSerializer,
                             RecipeAddUpdateSerializer,
                             RecipeGetSerializer, TagSerializer,
                             UserListSerializer,
                             UserAvatarSerializer)
from api.utils import add_favorite_shopping_cart, delete_favorite_shopping_cart
from recipes.models import (Ingredient, RecipeIngredient, Favorite,
                            Follow, Recipe, ShoppingCart, Tag)


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
                serializer = UserAvatarSerializer(
                    request.user,
                    data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
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
        recipes_limit = request.query_params.get('recipes_limit')
        kwargs['recipes_limit'] = recipes_limit
        subscriptions = Follow.objects.filter(user=request.user)
        paginator = FoodgramPaginator()
        paginated_subscriptions = paginator.paginate_queryset(
            subscriptions, request
        )
        serializer = FollowSerializer(paginated_subscriptions,
                                      many=True,
                                      **kwargs)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=('post', 'delete',),
            url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Подписка на пользователя
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        following = get_object_or_404(User, id=kwargs.pop('id'))
        recipes_limit = request.query_params.get('recipes_limit')
        kwargs['recipes_limit'] = recipes_limit

        if request.method == 'POST':
            if Follow.objects.filter(user=user,
                                     following=following).exists():
                return Response(
                    data={'Error': f'Вы уже подписаны на {user.username}!'},
                    status=status.HTTP_400_BAD_REQUEST)

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
                raise ValidationError(f'Вы не подписаны на {user.username}!')

            Follow.objects.get(user=user,
                               following=following).delete()
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

    @action(detail=True, methods=('get', ),
            permission_classes=(permissions.AllowAny, ),
            url_path='get-link')
    # Получение короткой ссылки на рецепт
    def get_short_link(self, recipe):
        return {'slug': recipe.slug}

    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление в избранное
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            if Favorite.objects.filter(user=user,
                                           recipe=recipe).exists():
                raise ValidationError('Вы уже добавили рецепт в избранное')
            Favorite.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_201_CREATED)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление рецепта в корзину
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user,
                                           recipe=recipe).exists():
                raise ValidationError('Вы уже добавили рецепт в избранное')
            ShoppingCart.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_201_CREATED)

    @action(methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    # Скачивание ингредиентов для рецептов, добавленных в корзину
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(quantity=Sum('amount'))

        document = ap.Document()

        page = document.pages.add()

        for ingredient in ingredients:
            text_fragment = ap.text.TextFragment(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["quantity"]}, '
                f'{ingredient["ingredient__measurement_unit"]}')
            page.paragraphs.add(text_fragment)
            document.save('output.pdf')

        response = HttpResponse(document, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="output.pdf"'
        return response


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
