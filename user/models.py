from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('agent', 'Customer')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')
    created_at = models.DateTimeField(auto_now_add = True , null= True)
    updated_at = models.DateTimeField(auto_now= True)
    # Add these to resolve the reverse accessor clash
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="core_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_permissions",
        related_query_name="user",
    )

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]




class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return self.name
    

