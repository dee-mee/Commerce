from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
import json
from django.db.models import F
from django.utils import timezone
from store.models import Product, ProductVariant, FlashSale, FlashSaleItem
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


@require_POST
def cart_add_ajax(request, product_id):
    """
    Add a product to the cart via AJAX
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        override_quantity = data.get('override', False)
        variant_id = data.get('variant', None)
        flash_sale_item_id = data.get('flash_sale_item_id', None)
        
        # Check if this is a flash sale item
        flash_sale_item = None
        if flash_sale_item_id:
            try:
                now = timezone.now()
                flash_sale_item = FlashSaleItem.objects.select_related('flash_sale').get(
                    id=flash_sale_item_id,
                    product=product,
                    flash_sale__is_active=True,
                    flash_sale__start_time__lte=now,
                    flash_sale__end_time__gte=now
                )
                
                # Check if flash sale item has stock
                if flash_sale_item.stock_quantity < quantity:
                    return JsonResponse({
                        'success': False,
                        'error': f'Sorry, only {flash_sale_item.stock_quantity} items left in this flash sale.',
                        'stock_quantity': flash_sale_item.stock_quantity
                    })
            except FlashSaleItem.DoesNotExist:
                flash_sale_item = None
        
        # If not a flash sale or flash sale item doesn't exist, check regular stock
        if not flash_sale_item:
            # Check if variant exists and belongs to the product
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    # Check if variant has stock
                    if variant.stock_override is not None and variant.stock_override < quantity:
                        return JsonResponse({
                            'success': False,
                            'error': f'Sorry, only {variant.stock_override} items in stock for this variant.'
                        })
                except ProductVariant.DoesNotExist:
                    variant_id = None
            
            # Check if product has stock
            if not variant_id and product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Sorry, only {product.stock} items in stock.'
                })
        
        # Add product to cart
        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=override_quantity,
            variant_id=variant_id
        )
        
        # Update flash sale item stock if applicable
        if flash_sale_item:
            # Atomically decrement the stock to prevent race conditions
            FlashSaleItem.objects.filter(id=flash_sale_item.id).update(
                stock_quantity=F('stock_quantity') - quantity
            )
            
            # Get the updated stock quantity
            updated_item = FlashSaleItem.objects.get(id=flash_sale_item.id)
            remaining_stock = updated_item.stock_quantity
            remaining_percentage = updated_item.get_remaining_percentage()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to your cart.',
                'cart_count': len(cart),
                'is_flash_sale': True,
                'remaining_stock': remaining_stock,
                'remaining_percentage': remaining_percentage
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to your cart.',
            'cart_count': len(cart)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
