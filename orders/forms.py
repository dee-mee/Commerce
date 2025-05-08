from django import forms
from .models import Order, ReturnRequest

class OrderCreateForm(forms.ModelForm):
    """Form for creating a new order"""
    address_id = forms.IntegerField(widget=forms.HiddenInput())
    shipping_method = forms.IntegerField(widget=forms.HiddenInput())
    
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special instructions for delivery'}),
        }

class ReturnRequestForm(forms.ModelForm):
    """Form for creating a return request"""
    class Meta:
        model = ReturnRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please explain why you want to return this order'}),
        }
