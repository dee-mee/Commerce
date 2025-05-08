from django.db import models
from django.conf import settings
from store.models import Product, ProductVariant

class Cart(models.Model):
    """
    Shopping cart model for logged in users
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        return sum(item.get_total_price() for item in self.items.all())

class CartItem(models.Model):
    """
    Shopping cart item model
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product', 'variant')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_unit_price(self):
        if self.variant and self.variant.price_override:
            return self.variant.price_override
        return self.product.get_price()
    
    def get_total_price(self):
        return self.get_unit_price() * self.quantity
