from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = SimpleRouter()

router.register(
    r'recipes', RecipeViewSet, basename='recipes'
)
router.register(
    r'ingredients', IngredientViewSet, basename='ingredients'
)
router.register(
    r'tags', TagViewSet, basename='tags'
)

authpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken'))
]

urlpatterns = [
    path('', include(router.urls)),
] + authpatterns
