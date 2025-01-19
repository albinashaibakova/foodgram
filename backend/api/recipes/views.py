from django.db.models import Sum
from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework import (filters, permissions,
                            status, viewsets)
from rest_framework.response import Response
import aspose.pdf as ap
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse

from recipes.models import (Ingredient, IngredientRecipe,
                                    Recipe, ShoppingCart, Tag, Favorite)
from shortener.models import LinkShortener
from api.shortener.serializers import ShortenerSerializer
from api.recipes.serializers import (IngredientSerializer, FavoriteSerializer,
                                     RecipeAddUpdateSerializer,
                                     RecipeGetSerializer, TagSerializer,
                                     ShoppingCartSerializer)
from api.permissions import IsOwnerOrReadOnly

from api.utils import add_favorite_shopping_cart, delete_favorite_shopping_cart

from api.filtersets import RecipeFilterSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    search_fields = ('author.id', 'tags', 'user.favorites')
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet


    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return RecipeAddUpdateSerializer
        return RecipeGetSerializer

    @action(detail=True, methods=('get', ),
            permission_classes=(permissions.AllowAny, ),
            url_path='get-link')
    def get_short_link(self, request, pk=None, **kwargs):
        long_url = self.request.build_absolute_uri()
        if not LinkShortener.objects.filter(long_url=long_url).exists():
            serializer = ShortenerSerializer(data={'long_url': long_url})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        slug = LinkShortener.objects.get(long_url=long_url).slug
        return redirect(reverse('shortener:short_link', kwargs={'slug':slug}))

    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated, ),
            detail=True)
    def favorite(self, request, *args, **kwargs):
        kwargs['recipe_id'] = kwargs['pk']
        serializer = FavoriteSerializer

        if request.method == 'POST':
            return Response(add_favorite_shopping_cart(request, serializer, **kwargs),
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            model_instance = Favorite
            if delete_favorite_shopping_cart(request, model_instance, **kwargs):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        kwargs['recipe_id'] = kwargs['pk']
        serializer = ShoppingCartSerializer

        if request.method == 'POST':
            return Response(add_favorite_shopping_cart(request, serializer, **kwargs),
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            model_instance = ShoppingCart
            if delete_favorite_shopping_cart(request, model_instance, **kwargs):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name',
                 'ingredient__measurement_unit').annotate(quantity=Sum('amount'))

        document = ap.Document()

        page = document.pages.add()

        for ingredient in ingredients:
            text_fragment = ap.text.TextFragment(
                f'{ingredient["ingredient__name"]} - {ingredient["quantity"]}, '
                f'{ingredient["ingredient__measurement_unit"]}')
            page.paragraphs.add(text_fragment)
            document.save('output.pdf')

        response = HttpResponse(document, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="output.pdf"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None
