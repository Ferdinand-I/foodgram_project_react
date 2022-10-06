# Generated by Django 3.2 on 2022-10-06 19:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_recipe_shopping_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='favorited_users',
            field=models.ManyToManyField(related_name='favorited', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи, которые добавили рецепт в избранное'),
        ),
    ]