import io

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import RecipesFilters
from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (AddRecipeSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)


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
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilters
    search_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def recipe_in_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            item = Favorite.objects.get(user=user,
                                        recipe=recipe
                                        )
            if request.method == 'DELETE':
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if request.method == 'POST':
                return Response({'error': 'Этот рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
        except Favorite.DoesNotExist:
            if request.method == 'DELETE':
                return Response({'error': 'Этого рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            if request.method == 'POST':
                if user.id == recipe.author_id:
                    return Response({'error': 'Нельзя добавить свой рецепт'},
                                    status=status.HTTP_400_BAD_REQUEST
                                    )
                item = Favorite(user=user,
                                recipe=recipe
                                )
                item.save()
                serializer = AddRecipeSerializer(
                    item,
                    context={'request': request}
                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            url_path='shopping_cart', permission_classes=(IsAuthorOrAdmin,))
    def recipe_in_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            item = ShoppingCart.objects.get(user=user,
                                            recipe=recipe
                                            )
            if request.method == 'DELETE':
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if request.method == 'POST':
                return Response({'error': 'Этот рецепт уже в корзине'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
        except ShoppingCart.DoesNotExist:
            if request.method == 'DELETE':
                return Response({'error': 'Этого рецепта нет в корзине'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            if request.method == 'POST':
                item = ShoppingCart(user=user,
                                    recipe=recipe
                                    )
                item.save()
                serializer = AddRecipeSerializer(
                    item,
                    context={'request': request}
                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if not shopping_cart:
            return HttpResponse("Ваша корзина пуста")
        ingredient_dict = {}
        for item in shopping_cart:
            recipe = item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=recipe).values('ingredient__name',
                                      'ingredient__measurement_unit',
                                      'quantity'
                                      )
            for ingredient in recipe_ingredients:
                key = (ingredient['ingredient__name']+' ('
                       + ingredient['ingredient__measurement_unit']+')'
                       )
                if ingredient['ingredient__name'] in ingredient_dict:
                    ingredient_dict[key] += ingredient['quantity']
                else:
                    ingredient_dict[key] = ingredient['quantity']
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setFont('ArialUni', 20)
        pdf.drawString(200, 750, 'Список покупок')
        pdf.setFont('ArialUni', 16)
        y = 710
        for i, (keys, value) in enumerate(ingredient_dict.items()):
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
