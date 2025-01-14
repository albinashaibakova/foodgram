from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework import (filters, permissions,
                            status, viewsets)
from rest_framework.response import Response
import aspose.pdf as ap
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, Favourite)

from .serializers import (IngredientSerializer, FavouriteSerializer,
                          RecipeAddUpdateSerializer,
                          RecipeGetSerializer, TagSerializer, ShoppingCartSerializer)
from .permissions import IsOwnerOrReadOnly



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    search_fields = ('author.id', 'tags', 'user.favourites')
    permission_classes = (IsOwnerOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return RecipeAddUpdateSerializer
        return RecipeGetSerializer


    @action(detail=True, methods=('get', ),
            permission_classes=(permissions.AllowAny, ),
            url_path='get-link')
    def get_short_link(self, request, pk=None):
        pass


    @action(methods=('post', 'delete'),
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated, ),
            detail=True)
    def favorite(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = FavouriteSerializer(
                data={
                    'user': request.user.id,
                    'recipe': get_object_or_404(Recipe, id=kwargs['pk']).id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Favourite.objects.filter(
                    user=request.user,
                    recipe=get_object_or_404(Recipe, id=kwargs['pk'])).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            favourite = get_object_or_404(Favourite,
                                          recipe=get_object_or_404(Recipe, id=kwargs['pk']),
                                          user=request.user)
            favourite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete'),
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={
                    'user': request.user.id,
                    'recipe': get_object_or_404(Recipe, id=kwargs['pk']).id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=get_object_or_404(Recipe, id=kwargs['pk'])).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            shopping_cart = ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=get_object_or_404(Recipe, id=kwargs['pk']))
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
