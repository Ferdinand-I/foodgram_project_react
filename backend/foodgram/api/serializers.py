from rest_framework import serializers

from core.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    name = serializers.ChoiceField(
        choices=((1, 'qwe'), )
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measure',
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientSerializer()

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        pass
