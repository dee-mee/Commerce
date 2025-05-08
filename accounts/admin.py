from django.contrib import admin
from .models import User, Address, VendorProfile

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_customer', 'is_vendor', 'is_staff')
    list_filter = ('is_customer', 'is_vendor', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Custom Fields', {'fields': ('is_customer', 'is_vendor', 'is_admin')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Override get_fieldsets to use this attribute when creating a user
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (None, {
                    'classes': ('wide',),
                    'fields': ('username', 'email', 'password1', 'password2', 'is_customer', 'is_vendor', 'is_admin', 'phone'),
                }),
            )
        return super().get_fieldsets(request, obj)

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = ('user__username', 'full_name', 'city', 'state')

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'approved', 'rating', 'created_at')
    list_filter = ('approved',)
    search_fields = ('store_name', 'user__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
