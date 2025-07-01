from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem, ShippingMethod, ReturnRequest
from .forms import OrderCreateForm, ReturnRequestForm
from cart.cart import Cart
from accounts.models import Address

@login_required
def order_create(request):
    """
    Create a new order
    """
    cart = Cart(request)
    
    # Check if cart is empty
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    # Get user's addresses
    addresses = Address.objects.filter(user=request.user)
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    # If user has no addresses, redirect to address creation
    if not addresses.exists():
        messages.warning(request, 'Please add a shipping address before proceeding to checkout')
        return redirect('accounts:address_create')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            
            # Get address
            address_id = form.cleaned_data['address_id']
            address = get_object_or_404(Address, id=address_id, user=request.user)
            order.address = address
            
            # Copy address details to order
            order.full_name = address.full_name
            order.email = request.user.email
            order.phone = address.phone
            order.address_line = address.address_line
            order.city = address.city
            order.state = address.state
            order.country = address.country
            order.postal_code = address.postal_code
            
            # Get shipping method
            shipping_method_id = form.cleaned_data['shipping_method']
            shipping_method = get_object_or_404(ShippingMethod, id=shipping_method_id, is_active=True)
            order.shipping_method = shipping_method
            order.shipping_amount = shipping_method.price
            
            # Calculate total
            from decimal import Decimal
            subtotal = Decimal(str(cart.get_subtotal()))
            tax_amount = subtotal * Decimal('0.1')  # 10% tax (example)
            total = subtotal + order.shipping_amount + tax_amount
            
            order.tax_amount = tax_amount
            order.total_amount = total
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    variant=item.get('variant'),
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            # Clear the cart
            cart.clear()
            
            # Redirect to payment
            return redirect('payment:process', order_id=order.id)
    else:
        # Pre-select default address if exists
        initial = {}
        default_address = addresses.filter(is_default=True, address_type='S').first()
        if default_address:
            initial['address_id'] = default_address.id
        
        form = OrderCreateForm(initial=initial)
    
    context = {
        'form': form,
        'cart': cart,
        'addresses': addresses,
        'shipping_methods': shipping_methods,
    }
    return render(request, 'orders/order_create.html', context)

@login_required
def order_list(request):
    """
    List all orders for the current user
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """
    Display order details
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be cancelled
    can_cancel = order.status == 'pending'
    
    # Check if return request can be made
    can_return = order.status == 'delivered' and not order.return_requests.exists()
    
    context = {
        'order': order,
        'can_cancel': can_cancel,
        'can_return': can_return,
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_cancel(request, order_id):
    """
    Cancel an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be cancelled
    if order.status != 'pending':
        messages.error(request, 'This order cannot be cancelled')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully')
        return redirect('orders:order_list')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_cancel.html', context)

@login_required
def return_request(request, order_id):
    """
    Create a return request for an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if return request can be made
    if order.status != 'delivered':
        messages.error(request, 'Return requests can only be made for delivered orders')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Check if return request already exists
    if order.return_requests.exists():
        messages.error(request, 'A return request already exists for this order')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            return_request = form.save(commit=False)
            return_request.order = order
            return_request.user = request.user
            return_request.save()
            messages.success(request, 'Return request submitted successfully')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = ReturnRequestForm()
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'orders/return_request.html', context)
