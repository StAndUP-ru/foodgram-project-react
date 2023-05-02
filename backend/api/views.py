import io

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag,
                            Favorite, ShoppingCart)
from users.models import Subscription, User
from .filters import RecipesFilters
from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (ShortRecipeSerializer, CreateRecipeSerializer,
                          CustomUserSerializer, IngredientSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)

pdfmetrics.registerFont(TTFont('ArialUni', 'fonts/Arial Unicode MS.ttf'))


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,))
    def user_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        try:
            subscription = Subscription.objects.get(
                user=user,
                author=author
            )
            if request.method == 'DELETE':
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы уже подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        except Subscription.DoesNotExist:
            if request.method == 'DELETE':
                return Response({'error': 'Вы не подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            if user == author:
                return Response({'error': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            subscription = Subscription(
                user=user,
                author=author
            )
            subscription.save()
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def user_subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilters
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def post_method(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,))
    def recipe_favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.post_method(request=request, pk=pk,
                                    serializers=FavoriteSerializer)
        return self.delete_method(request=request, pk=pk, model=Favorite)

    @action(detail=False, methods=['GET'], url_path='favorites',
            permission_classes=(permissions.IsAuthenticated,))
    def list_recipes_favorite(self, request, pk=None):
        user = request.user
        queryset = Favorite.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FavoriteSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def recipe_shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.post_method(request=request, pk=pk,
                                    serializers=ShoppingCartSerializer)
        return self.delete_method(request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['GET'], url_path='shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def list_shopping_cart(self, request, pk=None):
        user = request.user
        queryset = ShoppingCart.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ShoppingCartSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not ShoppingCart.objects.filter(user=user).exists():
            return HttpResponse("Ваш список покупок пуст")
        shopping_cart = ShoppingCart.objects.filter(user=user)
        ingredient_out: dict = {}
        for item in shopping_cart:
            recipe = item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=recipe).values('ingredient__name',
                                      'ingredient__measurement_unit',
                                      'amount'
                                      )
            for ingredient in recipe_ingredients:
                key = (ingredient['ingredient__name']+' ('
                       + ingredient['ingredient__measurement_unit']+')'
                       )
                if ingredient['ingredient__name'] in ingredient_out:
                    ingredient_out[key] += ingredient['amount']
                else:
                    ingredient_out[key] = ingredient['amount']
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setFont('ArialUni', 20)
        pdf.drawString(200, 750, 'Список покупок')
        pdf.setFont('ArialUni', 16)
        y = 710
        for i, (keys, value) in enumerate(ingredient_out.items()):
            item_string = f'{i+1}. {keys} - {value}'
            pdf.drawString(100, y, item_string)
            y -= 20
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.pdf'
                            )


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
