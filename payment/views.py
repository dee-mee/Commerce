from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse
from orders.models import Order, Payment
from .models import PaymentIntent
import uuid

@login_required
def payment_process(request, order_id):
    """
    Process payment for an order using a simplified mock payment system
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is already paid
    if order.payment_status == 'paid':
        messages.info(request, 'This order has already been paid')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Check if order is cancelled
    if order.status == 'cancelled':
        messages.error(request, 'This order has been cancelled')
        return redirect('orders:order_list')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            messages.error(request, 'Please select a payment method')
            return redirect('payment:process', order_id=order.id)
        
        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Create payment intent record
        payment_intent = PaymentIntent.objects.create(
            order=order,
            payment_intent_id=transaction_id,
            amount=order.total_amount,
            status='succeeded'
        )
        
        # Update order status
        order.status = 'processing'
        order.payment_status = 'paid'
        order.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            amount=payment_intent.amount,
            status='completed',
            transaction_id=transaction_id,
            paid_at=timezone.now()
        )
        
        messages.success(request, 'Payment successful! Your order is now being processed.')
        return redirect('payment:completed')
    
    context = {
        'order': order,
    }
    return render(request, 'payment/process.html', context)

def payment_completed(request):
    """
    Display payment completed page
    """
    return render(request, 'payment/completed.html')

def payment_cancelled(request):
    """
    Display payment cancelled page
    """
    return render(request, 'payment/cancelled.html')

@csrf_exempt
def payment_callback(request):
    """
    Handle payment callback for external payment systems
    This is a simplified mock function that would normally handle callbacks from payment processors
    """
    if request.method == 'POST':
        try:
            # In a real system, we would validate the callback data
            # and verify the payment status with the payment processor
            
            # For our mock system, we'll just check if the order_id is provided
            order_id = request.POST.get('order_id')
            if not order_id:
                return JsonResponse({'error': 'Order ID is required'}, status=400)
            
            # Get the order
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)
            
            # Check if the order is already paid
            if order.payment_status == 'paid':
                return JsonResponse({'status': 'Order already paid'}, status=200)
            
            # Get the payment intent
            try:
                payment_intent = PaymentIntent.objects.get(order=order)
            except PaymentIntent.DoesNotExist:
                # Create a new payment intent if it doesn't exist
                transaction_id = str(uuid.uuid4())
                payment_intent = PaymentIntent.objects.create(
                    order=order,
                    payment_intent_id=transaction_id,
                    amount=order.total_amount,
                    status='succeeded'
                )
            
            # Update payment intent status
            payment_intent.status = 'succeeded'
            payment_intent.save()
            
            # Update order status
            order.status = 'processing'
            order.payment_status = 'paid'
            order.save()
            
            # Create payment record
            Payment.objects.create(
                order=order,
                amount=payment_intent.amount,
                status='completed',
                transaction_id=payment_intent.payment_intent_id,
                paid_at=timezone.now()
            )
            
            return JsonResponse({'status': 'success'}, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
