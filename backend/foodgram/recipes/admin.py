from django.contrib import admin
from .models import Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe


@admin.register(Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe)
class UserAdmin(admin.ModelAdmin):
    pass
