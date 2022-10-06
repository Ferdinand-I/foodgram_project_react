from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT,
                                   HTTP_403_FORBIDDEN)
from rest_framework.viewsets import ModelViewSet

from recipes.models import Recipe, Ingredient, Tag
from users.models import User
from .filters import RecipeFilter
from .serializers import (RecipeSerializer, IngredientSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def get_current_user(self):
        return self.request.user

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, *args, **kwargs):
        current_user = self.request.user
        data = UserSerializer(current_user).data
        return Response(data)

    @action(
        detail=False,
        methods=['post', ]
    )
    def set_password(self, request, *args, **kwargs):
        if (request.data.get('new_password') and
                request.data.get('current_password')):
            current_user = self.get_current_user()
            current_pass = current_user.password
            if check_password(
                    request.data.get('current_password'), current_pass
            ):
                current_user.set_password(request.data.get('new_password'))
                current_user.save()
                return Response({'message': 'Password successfully changed'})
            else:
                return Response(
                    content_type='application/json',
                    data={'current_password': 'Wrong password'},
                    status=HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'message': 'Incoming data is no valid'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get', ],
        detail=False
    )
    def subscriptions(self, *args, **kwargs):
        pass


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def perform_create(self, serializer):
        cooking_time = serializer.initial_data['cooking_time']
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=self.request.user,
            cooking_time=cooking_time
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_current_user()
        obj = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        if obj:
            if user == obj.author:
                obj.delete()
                return Response(
                    content_type='application/JSON',
                    data={'message': 'Recipe is sucessfully deleted'},
                    status=HTTP_204_NO_CONTENT
                )
            return Response(
                content_type='application/JSON',
                data={
                    "detail": "У вас недостаточно прав "
                              "для выполнения данного действия."
                },
                status=HTTP_403_FORBIDDEN
            )

    def get_recipe(self):
        return Recipe.objects.get(pk=self.kwargs.get('pk'))

    def get_current_user(self):
        return self.request.user

    def small_recipe_representation(self):
        data = RecipeSerializer(self.get_recipe()).data
        return {
            "id": data['id'],
            "name": data['name'],
            "image": data['image'],
            "cooking_time": data['cooking_time']
        }

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, *args, **kwargs):
        recipe = self.get_recipe()
        user = self.get_current_user()
        if self.request.method == 'POST':
            if user not in recipe.shopping_users.all():
                recipe.shopping_users.add(user)
                return Response(self.small_recipe_representation())
            else:
                return Response(
                    content_type='application/JSON',
                    data={'error': 'Item is already in shopping cart'},
                    status=HTTP_400_BAD_REQUEST
                )
        if user in recipe.shopping_users.all():
            recipe.shopping_users.remove(user)
            return Response(
                {'message': 'Item is succefully removed from your '
                            'shopping cart'},
                status=HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'message': 'Item is not in your shopping cart'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(
        url_path='download_shopping_cart',
        detail=False,
        methods=['get', ]
    )
    def download_shopping_cart(self, *args, **kwargs):
        return Response(content_type='application/pdf')

    @action(
        url_path='favorite',
        detail=True,
        methods=['post', 'delete', ]
    )
    def favorite(self, *args, **kwargs):
        recipe = self.get_recipe()
        user = self.get_current_user()
        if self.request.method == 'POST':
            if user not in recipe.favorited_users.all():
                recipe.favorited_users.add(user)
                return Response(self.small_recipe_representation())
            else:
                return Response(
                    {'error': 'Item is already in favorited'},
                    status=HTTP_400_BAD_REQUEST
                )
        if user in recipe.favorited_users.all():
            recipe.favorited_users.remove(user)
            return Response(
                {'message': 'Item is succefully removed from your '
                            'favorited'},
                status=HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'message': 'Item is not in your favorited'},
                status=HTTP_400_BAD_REQUEST
            )


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['^name', ]


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
