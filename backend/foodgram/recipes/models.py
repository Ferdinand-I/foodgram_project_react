from django.db import models
from users.models import User


CHOICES = (

)


class Ingredient(models.Model):
    """Class that represents Ingredients model."""
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    measure = models.CharField(
        max_length=15,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Class that represents Tags model."""
    name = models.CharField(
        max_length=50,
        verbose_name='Тэг',
        unique=True
    )
    color = models.CharField(
        max_length=16,
        verbose_name='Цвет',
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Class that represents Recipes model."""
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        related_name='recipes',
        null=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
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
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Class that represents schema of
    Ingredient and Recipe models relations.
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    """Class that represents schema of Tag and Recipe models relations."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'
