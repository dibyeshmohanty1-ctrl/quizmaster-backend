from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("STUDENT", "Student"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="STUDENT"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username