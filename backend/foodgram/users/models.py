from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Class that represents User model."""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
