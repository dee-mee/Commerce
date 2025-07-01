from django.contrib import admin
from django.db.models import Avg, Count
from django.utils import timezone
from django.utils.html import format_html

from .models import Category, Brand, Product, ProductImage, ProductVariant, Review, ReviewImage, FlashSale, FlashSaleItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'vendor', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'brand', 'vendor')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    list_editable = ('price', 'stock', 'is_active')
    autocomplete_fields = ['category', 'brand', 'vendor']
    search_fields = ('name', 'description', 'sku')
    list_per_page = 20

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating')
    search_fields = ('product__name', 'user__username', 'comment')
    inlines = [ReviewImageInline]
    list_editable = ('approved',)

class FlashSaleItemInline(admin.TabularInline):
    model = FlashSaleItem
    extra = 1
    fields = ('product', 'discount_percentage', 'flash_sale_price', 'original_price', 'stock_quantity', 'initial_stock_quantity', 'get_remaining_percentage')
    readonly_fields = ('original_price', 'get_remaining_percentage')
    autocomplete_fields = ['product']
    
    def get_remaining_percentage(self, obj):
        if obj.id:
            percentage = obj.get_remaining_percentage()
            return format_html(
                '<div style="width:100px; height:10px; background-color:#f8f9fa; border-radius:5px;">' 
                '<div style="width:{}px; height:10px; background-color:{}; border-radius:5px;"></div></div>' 
                '{} items left ({}%)',
                percentage,
                '#28a745' if percentage > 50 else '#ffc107' if percentage > 20 else '#dc3545',
                obj.stock_quantity,
                percentage
            )
        return "-"
    get_remaining_percentage.short_description = 'Stock Status'

class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active', 'is_ongoing', 'time_left_display', 'get_items_count', 'get_sale_status')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('title', 'description')
    inlines = [FlashSaleItemInline]
    list_editable = ('is_active',)
    actions = ['duplicate_flash_sale']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time'),
            'description': 'Set the start and end times for the flash sale'
        }),
    )
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Products'
    
    def get_sale_status(self, obj):
        now = timezone.now()
        if obj.is_ongoing():
            return format_html('<span style="color: #28a745;"><b>Active</b></span>')
        elif obj.start_time > now:
            return format_html('<span style="color: #17a2b8;"><b>Upcoming</b></span>')
        else:
            return format_html('<span style="color: #dc3545;"><b>Ended</b></span>')
    get_sale_status.short_description = 'Status'
    
    def duplicate_flash_sale(self, request, queryset):
        for flash_sale in queryset:
            # Create a new flash sale with the same details but different timing
            new_sale = FlashSale.objects.create(
                title=f"Copy of {flash_sale.title}",
                description=flash_sale.description,
                start_time=timezone.now() + timezone.timedelta(days=1),  # Start tomorrow
                end_time=timezone.now() + timezone.timedelta(days=2),    # End in 2 days
                is_active=False  # Set to inactive by default
            )
            
            # Duplicate all items
            for item in flash_sale.items.all():
                FlashSaleItem.objects.create(
                    flash_sale=new_sale,
                    product=item.product,
                    discount_percentage=item.discount_percentage,
                    flash_sale_price=item.flash_sale_price,
                    original_price=item.original_price,
                    stock_quantity=item.initial_stock_quantity,  # Use initial stock
                    initial_stock_quantity=item.initial_stock_quantity
                )
        
        self.message_user(request, f"{len(queryset)} flash sale(s) duplicated successfully.")
    duplicate_flash_sale.short_description = "Duplicate selected flash sales"

class FlashSaleItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'flash_sale', 'discount_percentage', 'original_price', 'flash_sale_price', 'stock_quantity', 'items_left')
    list_filter = ('flash_sale',)
    search_fields = ('product__name', 'flash_sale__title')
    autocomplete_fields = ['product', 'flash_sale']
    readonly_fields = ('original_price',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(FlashSale, FlashSaleAdmin)
admin.site.register(FlashSaleItem, FlashSaleItemAdmin)
