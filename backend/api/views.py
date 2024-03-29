import io
import os

from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.settings import BASE_DIR
from users.models import Subscription, User
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from .filters import RecipesFilters, IngredientFilter
from .paginations import LimitPageNumberPagination, CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)

FONT_PATH = os.path.join(BASE_DIR, '/app/backend_static/fonts/Arial.TTF')


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
    pagination_class = CustomPagination
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
            return HttpResponse('Ваш список покупок пуст')
        shopping_cart = ShoppingCart.objects.filter(
            user=user
        ).values_list('recipe', flat=True)
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart
        ).select_related('ingredient').values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        pdfmetrics.registerFont(TTFont('ArialUni', FONT_PATH))
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setFont('ArialUni', 20)
        pdf.drawString(200, 750, 'Список покупок')
        pdf.setFont('ArialUni', 16)
        y = 710
        for i, item in enumerate(recipe_ingredients):
            name_unit = item[0] + ' (' + item[1] + ')'
            total_amount = item[2]
            item_string = f'{i+1}. {name_unit} - {total_amount}'
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
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
