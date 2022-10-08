import io

from django.contrib.auth.hashers import check_password
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED)
from rest_framework.viewsets import ModelViewSet

from recipes.models import Recipe, Ingredient, Tag
from users.models import User
from .filters import RecipeFilter
from .permissions import IsAuthor
from .serializers import (RecipeSerializer, IngredientSerializer,
                          TagSerializer, UserSerializer,
                          SubscriptionSerializer,
                          RecipeSmallReadOnlySerialiazer)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def get_permissions(self):
        if len(self.request.path.split('/')) != 5:
            permission_classes = [AllowAny, ]
        else:
            permission_classes = [IsAuthenticated, ]
        return [permission() for permission in permission_classes]

    def get_current_user(self) -> User:
        return self.request.user

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ],
    )
    def me(self, *args, **kwargs):
        current_user = self.request.user
        data = UserSerializer(current_user).data
        data['is_subscribed'] = False
        return Response(
            data
        )

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
                return Response({'message': 'Password successfully changed.'})
            else:
                return Response(
                    content_type='application/json',
                    data={'current_password': 'Wrong password.'},
                    status=HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'message': 'Incoming data is not valid.'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['post', 'delete', ],
        detail=True
    )
    def subscribe(self, *args, **kwargs):
        current_user = self.get_current_user()
        obj = get_object_or_404(User, pk=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            if current_user != obj:
                if current_user not in obj.subscribers.all():
                    obj.subscribers.add(current_user)
                    data = SubscriptionSerializer(obj).data
                    data['is_subscribed'] = True
                    return Response(
                        data=data,
                        status=HTTP_201_CREATED
                    )
                else:
                    return Response(
                        data={'error': 'You have already subscribed '
                                       'to this user.'},
                        status=HTTP_400_BAD_REQUEST
                    )
            return Response(
                data={'error': 'Yor cannot subscribe to yourself.'},
                status=HTTP_400_BAD_REQUEST
                    )
        if current_user != obj:
            if current_user in obj.subscribers.all():
                obj.subscribers.remove(current_user)
                return Response(
                    data={'message': 'You have sucessfully '
                                     'unsubscriped from the user.'},
                    status=HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    data={'error': 'You even have not subscribed yet.'},
                    status=HTTP_400_BAD_REQUEST
                )
        return Response(
            status=HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, *args, **kwargs):
        user_subscriptions = self.get_current_user().subscriptions.all()
        return Response(
            data=[SubscriptionSerializer(subscription).data
                  for subscription in user_subscriptions]
        )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor, ]
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

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('pk'))

    def get_current_user(self):
        return self.request.user

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
                return Response(
                    RecipeSmallReadOnlySerialiazer(self.get_recipe()).data
                )
            else:
                return Response(
                    data={'error': 'Item is already in shopping cart.'},
                    status=HTTP_400_BAD_REQUEST
                )
        if user in recipe.shopping_users.all():
            recipe.shopping_users.remove(user)
            return Response(
                {'message': 'Item is succefully removed from your '
                            'shopping cart.'},
                status=HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Item is not in your shopping cart.'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get', ]
    )
    def download_shopping_cart(self, *args, **kwargs):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        textobject = pdf.beginText(10, 10)
        textobject.setTextOrigin(10, 10)

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

    @action(
        detail=True,
        methods=['post', 'delete', ]
    )
    def favorite(self, *args, **kwargs):
        recipe = self.get_recipe()
        user = self.get_current_user()
        if self.request.method == 'POST':
            if user not in recipe.favorited_users.all():
                recipe.favorited_users.add(user)
                return Response(
                    RecipeSmallReadOnlySerialiazer(self.get_recipe()).data
                )
            else:
                return Response(
                    {'error': 'Item is already in favorited.'},
                    status=HTTP_400_BAD_REQUEST
                )
        if user in recipe.favorited_users.all():
            recipe.favorited_users.remove(user)
            return Response(
                {'message': 'Item is succefully removed from your '
                            'favorited.'},
                status=HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Item even is not in your favorited yet.'},
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
    http_method_names = ['get', ]
