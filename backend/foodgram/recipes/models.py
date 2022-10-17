from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class Ingredient(models.Model):
    """Class that represents Ingredients model."""
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        db_index=True
    )
    measure = models.CharField(
        max_length=15,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measure}'


class Tag(models.Model):
    """Class that represents Tags model."""
    name = models.CharField(
        max_length=50,
        verbose_name='Тэг',
        unique=True,
    )
    color = models.CharField(
        max_length=16,
        verbose_name='Цвет',
        unique=True
    )
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        ordering = ['color']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Class that represents Recipes model."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        db_index=True
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги',
        db_index=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Cooking time cannot be less than "1".')
        ]
    )
    created = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )
    shopping_users = models.ManyToManyField(
        User,
        verbose_name='Пользователи, которые добавили рецепт в корзину'
    )
    favorited_users = models.ManyToManyField(
        User,
        verbose_name='Пользователи, которые добавили рецепт в избранное',
        related_name='favorited'
    )

    class Meta:
        # Ordering meta param also redefines while
        # one of view functions' method works. If redefine here check
        # api/views.py RecipeViewSet method 'download_shopping_cart'.
        ordering = ['-created']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Class that represents schema of
    Ingredient and Recipe models relations.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    amount = models.IntegerField(
        validators=[MinValueValidator(1, 'Amount cannot be less than "1".')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.recipe.author} recipe {self.ingredient.name}'


class TagRecipe(models.Model):
    """Class that represents schema of Tag and Recipe models relations."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэг в рецепте'
        verbose_name_plural = 'Тэги в рецептах'

    def __str__(self):
        return f'{self.tag} {self.recipe}'
