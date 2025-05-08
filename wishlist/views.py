from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from store.models import Product
from .models import Wishlist

@login_required
def wishlist_detail(request):
    """
    Display the user's wishlist
    """
    # Get or create the user's wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    context = {
        'wishlist': wishlist,
        'products': wishlist.products.all(),
    }
    return render(request, 'wishlist/wishlist_detail.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """
    Add a product to the user's wishlist
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if the product is already in the wishlist
    if product in wishlist.products.all():
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            wishlist_count = wishlist.products.count()
            return JsonResponse({
                'success': True,
                'added': False,
                'message': f'{product.name} is already in your wishlist.',
                'product_id': product_id,
                'in_wishlist': True,
                'wishlist_count': wishlist_count
            })
        # Otherwise, redirect with a message
        messages.info(request, f'{product.name} is already in your wishlist.')
        return redirect('store:product_detail', slug=product.slug)
    
    # Add the product to the wishlist
    wishlist.products.add(product)
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist_count = wishlist.products.count()
        return JsonResponse({
            'success': True,
            'added': True,
            'message': f'{product.name} added to your wishlist.',
            'product_id': product_id,
            'in_wishlist': True,
            'wishlist_count': wishlist_count
        })
    
    # Otherwise, redirect with a message
    messages.success(request, f'{product.name} added to your wishlist.')
    return redirect('store:product_detail', slug=product.slug)

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """
    Remove a product from the user's wishlist
    """
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    # Check if the product is in the wishlist
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            wishlist_count = wishlist.products.count()
            return JsonResponse({
                'success': True,
                'removed': True,
                'message': f'{product.name} removed from your wishlist.',
                'product_id': product_id,
                'in_wishlist': False,
                'wishlist_count': wishlist_count
            })
        
        # Otherwise, redirect with a message
        messages.success(request, f'{product.name} removed from your wishlist.')
    else:
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            wishlist_count = wishlist.products.count()
            return JsonResponse({
                'success': False,
                'message': f'{product.name} is not in your wishlist.',
                'product_id': product_id,
                'in_wishlist': False,
                'wishlist_count': wishlist_count
            })
        
        # Otherwise, redirect with a message
        messages.error(request, f'{product.name} is not in your wishlist.')
    
    # If the request came from the wishlist page, redirect back there
    if 'wishlist' in request.META.get('HTTP_REFERER', ''):
        return redirect('wishlist:wishlist_detail')
    
    # Otherwise, redirect to the product detail page
    return redirect('store:product_detail', slug=product.slug)

@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """
    Toggle a product in the user's wishlist (add if not present, remove if present)
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if the product is already in the wishlist
    if product in wishlist.products.all():
        # Remove the product from the wishlist
        wishlist.products.remove(product)
        added = False
        message = f'{product.name} removed from your wishlist.'
    else:
        # Add the product to the wishlist
        wishlist.products.add(product)
        added = True
        message = f'{product.name} added to your wishlist.'
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist_count = wishlist.products.count()
        return JsonResponse({
            'success': True,
            'added': added,
            'message': message,
            'product_id': product_id,
            'in_wishlist': added,
            'wishlist_count': wishlist_count
        })
    
    # Otherwise, redirect with a message
    if added:
        messages.success(request, message)
    else:
        messages.info(request, message)
    
    # If the request came from the wishlist page, redirect back there
    if 'wishlist' in request.META.get('HTTP_REFERER', ''):
        return redirect('wishlist:wishlist_detail')
    
    # Otherwise, redirect to the product detail page
    return redirect('store:product_detail', slug=product.slug)

@login_required
def check_wishlist_status(request, product_id):
    """
    Check if a product is in the user's wishlist
    """
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        in_wishlist = product in wishlist.products.all()
        wishlist_count = wishlist.products.count()
    except Wishlist.DoesNotExist:
        in_wishlist = False
        wishlist_count = 0
    
    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'product_id': product_id,
        'wishlist_count': wishlist_count
    })
