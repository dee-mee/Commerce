from django.contrib import admin
from .models import Order, OrderItem, ShippingMethod, DeliveryTracking, Payment, PaymentMethod, ReturnRequest

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variant']
    extra = 0

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0

class DeliveryTrackingInline(admin.StackedInline):
    model = DeliveryTracking
    extra = 0

class ReturnRequestInline(admin.TabularInline):
    model = ReturnRequest
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'full_name', 'tracking_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline, DeliveryTrackingInline, ReturnRequestInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Information', {
            'fields': ('address', 'address_line', 'city', 'state', 'country', 'postal_code')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'shipping_amount', 'tax_amount', 'status', 'payment_status', 'shipping_method', 'tracking_number', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'user__username', 'reason')
    readonly_fields = ('created_at',)

admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingMethod, ShippingMethodAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(ReturnRequest, ReturnRequestAdmin)
