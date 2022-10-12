from rest_framework import serializers
from django.shortcuts import get_object_or_404
from core.fields import Base64ImageField
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe
from users.models import User


class RecipeSmallReadOnlySerialiazer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]
        read_only_fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeSmallReadOnlySerialiazer(many=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_recipes_count(self, obj: User):
        return len(obj.recipes.all())


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug',
        ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measure',
        ]


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        ]
        read_only_fields = ['id', ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user in obj.subscribers.all()


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(
        source='ingredient.pk',
        write_only=True,
    )
    name = serializers.CharField(source='ingredient', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measure', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = [
            'pk',
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]
        extra_kwargs = {
            'amount': {'required': True},
            'id': {'required': True}
        }

    def validate(self, attrs):
        amount = attrs.get('amount')
        if not amount:
            raise serializers.ValidationError(
                'Amount value must be define.'
            )
        if amount < 1:
            raise serializers.ValidationError(
                'Amount value must be greate than zero.'
            )
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
        required=False
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        required=False
    )
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set',
        many=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name')
            )
        ]

    def validate(self, attrs):
        cooking_time = attrs.get('cooking_time')
        if self.context.get('request').method != 'PATCH':
            if cooking_time is None or cooking_time < 1:
                raise serializers.ValidationError(
                    'Cooking time value is not valid.'
                )
            return attrs
        if cooking_time is None:
            return attrs
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Cooking time value must be greate than zero.'
            )
        return attrs

    def create(self, validated_data):
        ingredient_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredient_set:
            current_ingredient_pk = ingredient.get('ingredient').get('pk')
            current_ingredient = Ingredient.objects.get(
                pk=current_ingredient_pk
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag,
                recipe=recipe
            )
        return recipe

    def update(self, instance: Recipe, validated_data):
        ingredients_set = validated_data.pop('ingredientrecipe_set', [])
        super(RecipeSerializer, self).update(instance, validated_data)
        data_ingredients = list()
        for index in range(len(ingredients_set)):
            ingredient = ingredients_set[index]
            if ingredient and ingredient.get('ingredient'):
                data_ingredients.append([get_object_or_404(
                        Ingredient, pk=ingredient.get('ingredient').get('pk')
                    ), ingredients_set[index].get('amount')])
        if data_ingredients:
            IngredientRecipe.objects.filter(recipe=instance).delete()
            for ingredient in data_ingredients:
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient[0],
                    amount=ingredient[1]
                )
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        new_tag_representation = list()
        for tag_id in ret['tags']:
            tag = get_object_or_404(Tag, pk=tag_id)
            serialized_data = TagSerializer(tag)
            new_tag_representation.append(serialized_data.data)
        ret['tags'] = new_tag_representation
        return ret

    def get_is_in_shopping_cart(self, obj):
        if self.context:
            user = self.context['request'].user
            return user in obj.shopping_users.all()
        return

    def get_is_favorited(self, obj):
        if self.context:
            user = self.context['request'].user
            return user in obj.favorited_users.all()
        return
