from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model that uses email as the primary identifier.
    Extends AbstractUser to add a fullname field.
    """
    fullname = models.CharField(max_length=255)
    
    # Email is unique and used for authentication (USERNAME_FIELD)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'fullname']

    def __str__(self):
        return self.email