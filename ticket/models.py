from django.db import models

from user.models import Customer, User

# Create your models here.
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('sold', 'Sold'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    sold_to = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True, blank=True, related_name="sold_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'created_at']),
            models.Index(fields=['created_at']),
        ]