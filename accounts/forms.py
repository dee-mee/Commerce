from django import forms
from django_countries.fields import CountryField
from .models import User, Address, VendorProfile

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    """Form for creating and updating addresses"""
    class Meta:
        model = Address
        fields = ['address_type', 'full_name', 'phone', 'address_line', 'city', 'state', 'country', 'postal_code', 'is_default']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VendorRegistrationForm(forms.ModelForm):
    """Form for vendor registration"""
    class Meta:
        model = VendorProfile
        fields = ['store_name', 'description', 'logo']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
