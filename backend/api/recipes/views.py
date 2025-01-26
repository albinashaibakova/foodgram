import aspose.pdf as ap
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (permissions,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filtersets import IngredientFilter, RecipeFilterSet
from api.permissions import IsOwnerOrReadOnly
from api.recipes.serializers import (IngredientSerializer, FavoriteSerializer,
                                     RecipeAddUpdateSerializer,
                                     RecipeGetSerializer, TagSerializer,
                                     ShoppingCartSerializer)
from api.shortener.serializers import ShortenerSerializer
from api.utils import add_favorite_shopping_cart, delete_favorite_shopping_cart
from recipes.models import (Ingredient, RecipeIngredient, Favorite,
                            Recipe, ShoppingCart, Tag)
from shortener.models import LinkShortener


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
    def get_short_link(self, request, pk=None, **kwargs):
        long_url = self.request.build_absolute_uri()
        if not LinkShortener.objects.filter(
                long_url=long_url
        ).exists():
            serializer = ShortenerSerializer(
                data={'long_url': long_url}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        slug = LinkShortener.objects.get(long_url=long_url).slug
        return redirect(reverse(
            'shortener:short_link',
            kwargs={'slug': slug}))

    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление в избранное
    def favorite(self, request, *args, **kwargs):
        kwargs['recipe_id'] = kwargs['pk']
        serializer = FavoriteSerializer

        if request.method == 'POST':
            return Response(add_favorite_shopping_cart(
                request, serializer, **kwargs
            ),
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            model_instance = Favorite
            if delete_favorite_shopping_cart(
                    request, model_instance, **kwargs
            ):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    # Добавление рецепта в корзину
    def shopping_cart(self, request, *args, **kwargs):
        kwargs['recipe_id'] = kwargs['pk']
        serializer = ShoppingCartSerializer

        if request.method == 'POST':
            return Response(add_favorite_shopping_cart(
                request, serializer, **kwargs
            ),
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            model_instance = ShoppingCart
            if delete_favorite_shopping_cart(
                    request, model_instance, **kwargs
            ):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
