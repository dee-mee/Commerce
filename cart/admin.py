from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'get_total_price')
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_total_quantity', 'get_subtotal', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = ('get_total_quantity', 'get_subtotal')
    inlines = [CartItemInline]
    
    def get_total_quantity(self, obj):
        return obj.get_total_quantity()
    get_total_quantity.short_description = 'Total Quantity'
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'

admin.site.register(Cart, CartAdmin)
