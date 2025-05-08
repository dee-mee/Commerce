from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, ProductVariant
from .cart import Cart
from .forms import CartAddProductForm

def cart_detail(request):
    """
    Display the cart and its items
    """
    cart = Cart(request)
    
    # Create a list of update forms for each item in the cart
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                'quantity': item['quantity'],
                'override': True,
                'variant': item.get('variant_id')
            }
        )
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        variant_id = cd.get('variant')
        
        # Check if variant exists and belongs to the product
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                # Check if variant has stock
                if variant.stock_override is not None and variant.stock_override < cd['quantity']:
                    messages.error(request, f'Sorry, only {variant.stock_override} items in stock for this variant.')
                    return redirect('store:product_detail', slug=product.slug)
            except ProductVariant.DoesNotExist:
                variant_id = None
        
        # Check if product has stock
        if not variant_id and product.stock < cd['quantity']:
            messages.error(request, f'Sorry, only {product.stock} items in stock.')
            return redirect('store:product_detail', slug=product.slug)
        
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
            variant_id=variant_id
        )
        
        messages.success(request, f'{product.name} added to your cart.')
    
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    """
    Update the quantity of a product in the cart
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.update(product_id=product_id, quantity=cd['quantity'])
        messages.success(request, 'Cart updated successfully.')
    
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    """
    Remove a product from the cart
    """
    cart = Cart(request)
    cart.remove(product_id)
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')
