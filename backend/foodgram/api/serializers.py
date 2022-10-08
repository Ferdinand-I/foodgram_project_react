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
        if self.context:
            user = self.context['request'].user
            return user in obj.subscribers.all()
        return

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(
        source='ingredient.pk',
        write_only=True
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

    def validate_cooking_time(self, value: int):
        if value < 1:
            raise serializers.ValidationError(
                "Cooking time value must be greater than zero."
            )

    def create(self, validated_data):
        ingredient_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredient_set:
            current_ingredient_pk = ingredient['ingredient']['pk']
            current_ingredient = Ingredient.objects.get(
                pk=current_ingredient_pk
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag,
                recipe=recipe
            )
        return recipe

    def update(self, instance: Recipe, validated_data):
        ingredients_set = validated_data['ingredientrecipe_set']
        data_ingredients = [
            [get_object_or_404(Ingredient, pk=i['ingredient']['pk']),
             i['amount']]
            for i in ingredients_set]
        instance.name = validated_data['name']
        instance.image = validated_data['image']
        instance.text = validated_data['text']
        instance.cooking_time = self.initial_data['cooking_time']
        IngredientRecipe.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()
        for i in data_ingredients:
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=i[0], amount=i[1]
            )
        for i in validated_data['tags']:
            TagRecipe.objects.create(recipe=instance, tag=i)
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        new_tag_representation = list()
        for tag_id in ret['tags']:
            tag = Tag.objects.get(pk=tag_id)
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
