from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        exclude_tags = Tag.objects.exclude(
            slug__in=[tag.slug for tag in value]
        )
        queryset = queryset.filter(
            tags__in=value
        ).exclude(
            tags__in=exclude_tags
        ).distinct()
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
