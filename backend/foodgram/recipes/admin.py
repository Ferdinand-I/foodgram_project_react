from django.contrib import admin
from .models import Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'created']
    search_fields = ['name', 'author__username', ]
    list_filter = ['author', 'name', 'tags']
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measure']
    search_fields = ['name', 'measure']
    list_filter = ['name', ]
