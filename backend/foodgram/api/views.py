from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import Recipe, Ingredient, Tag
from .filters import RecipeFilter
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def perform_create(self, serializer):
        cooking_time = serializer.initial_data['cooking_time']
        serializer.save(
            author=self.request.user,
            cooking_time=cooking_time
        )

    @action(
        url_path='shopping_cart',
        detail=True,
        methods=['post', 'delete']
    )
    def shopping_cart(self, *args, **kwargs):
        recipe = Recipe.objects.get(pk=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            data = RecipeSerializer(recipe).data
            return Response(
                {
                    "id": data['id'],
                    "name": data['name'],
                    "image": data['image'],
                    "cooking_time": data['cooking_time']
                }
            )
        return Response('Delete method')


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
