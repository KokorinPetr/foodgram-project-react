from django.contrib import admin

from .models import (
    Recipe, Tag, Ingredient,
    RecipeIngredient, Subscription, FavoriteRecipe,
    ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'name', 'image', 'text', 'cooking_time', 'pub_date'
    ]
    inlines = [RecipeIngredientInline]


admin.register(RecipeIngredient)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Subscription)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
