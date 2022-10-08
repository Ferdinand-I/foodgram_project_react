from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    """Class that represents User model."""
    email = models.EmailField(unique=True, max_length=254, null=False)
    username = models.CharField(
        validators=[validators.RegexValidator(regex=r'^[\w.@+-]+\Z')],
        unique=True,
        max_length=150,
        null=False
    )
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    password = models.CharField(max_length=150, null=False)
    subscriptions = models.ManyToManyField(
        to='self',
        related_name='subscribers',
        symmetrical=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username
