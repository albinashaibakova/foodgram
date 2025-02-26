from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
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
        request.user.avatar.delete()
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
        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if author == user:
            raise ValidationError('Вы не можете подписаться на себя!')
        follow, created = Follow.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            raise ValidationError(
                f'Вы не можете повторно подписаться '
                f'на пользователя {author.username}'
            )
        return Response(
            AuthorFollowRepresentSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED)


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
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError('Рецепт не найден')
        return Response(
            data={'short-link': request.build_absolute_uri(
                reverse('short_link', kwargs={'pk': pk})
            )
            }
        )

    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def favorite(self, request, *args, **kwargs):
        """Добавление в избранное"""
        pk = kwargs.get('pk')
        if request.method == 'POST':
            return self.add_favorite_shopping_cart(
                request,
                model=Favorite,
                pk=pk
            )
        return self.delete_favorite_shopping_cart(
            request,
            model=Favorite,
            pk=pk
        )

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление рецепта в корзину"""
        pk = self.kwargs.get('pk')
        if request.method == 'POST':
            return self.add_favorite_shopping_cart(
                request,
                model=ShoppingCart,
                pk=pk
            )
        return self.delete_favorite_shopping_cart(
            request,
            model=ShoppingCart,
            pk=pk
        )

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
        shopping_list = render_shopping_cart(
            recipes,
            ingredients
        )
        filename = f'shopping_list_{date.today().strftime("%d-%m-%Y")}.txt'
        return FileResponse(shopping_list,
                            filename=filename,
                            content_type='text/plain')

    def add_favorite_shopping_cart(self, request, model, pk):
        """Функция для добавления рецепта в избранное или в корзину"""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        instance, created = model.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            raise ValidationError(f'Рецепт {instance.recipe.name} '
                                  f'уже был добавлен')
        return Response(RecipeGetShortSerializer(instance.recipe).data,
                        status=status.HTTP_201_CREATED)

    def delete_favorite_shopping_cart(self, request, model, pk=None):
        """Функция для удаления рецепта из избранного или в корзины"""
        get_object_or_404(model, id=pk).delete()
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
