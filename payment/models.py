from django.db import models
from django.conf import settings
from orders.models import Order

class PaymentIntent(models.Model):
    """
    Payment intent model to track payment processing
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_intents')
    payment_intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Intent'
        verbose_name_plural = 'Payment Intents'
    
    def __str__(self):
        return f"Payment Intent for Order {self.order.id}"
