from django.contrib import admin
from .models import PaymentIntent

class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_intent_id', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('order__id', 'payment_intent_id')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(PaymentIntent, PaymentIntentAdmin)
