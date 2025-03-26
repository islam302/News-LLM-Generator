from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.CharField(max_length=255)
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User')
    )
    role = models.CharField(max_length=20, choices=ROLES, default='user')


