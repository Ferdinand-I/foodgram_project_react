from rest_framework.viewsets import ModelViewSet
from recipes.models import Recipe, Ingredient, Tag
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer
from .filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
