from django.db import models
from django.conf import settings
from store.models import Product

class Wishlist(models.Model):
    """
    Model to store user wishlists
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    products = models.ManyToManyField(Product, related_name='in_wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Wishlist"
