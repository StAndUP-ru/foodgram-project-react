from django_filters.rest_framework import filters, FilterSet

# from recipes.models import Recipe, Tag
from recipes.models import Recipe


class RecipesFilters(FilterSet):
    # tags = filters.MultipleChoiceFilter(
    #     field_name='tags__slug',
    #     choices=[(tag.slug, tag.name) for tag in Tag.objects.all()]
    # )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        # fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favoriting__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset
