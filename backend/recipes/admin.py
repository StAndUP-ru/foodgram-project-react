from django.contrib import admin

from .models import (Ingredient, Recipe, RecipeIngredient, Tag,
                     RecipeTag, ShoppingCart, Favorite)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class TagAdmin(admin.ModelAdmin):
    inlines = [RecipeTagInline]
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, RecipeTagInline]
    list_display = (
        'pk',
        'author',
        'name',
        'favorite_count_total'
    )

    def favorite_count_total(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    favorite_count_total.short_description = 'Добавлений в избранное'

    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user',)


admin.site.register(ShoppingCart, ShoppingCartAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user',)


admin.site.register(Favorite, FavoriteAdmin)
