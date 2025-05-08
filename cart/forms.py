from django import forms
from store.models import ProductVariant

class CartAddProductForm(forms.Form):
    """Form for adding products to cart"""
    quantity = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'value': 1,
            'min': 1
        })
    )
    override = forms.BooleanField(
        required=False, 
        initial=False, 
        widget=forms.HiddenInput
    )
    variant = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )
