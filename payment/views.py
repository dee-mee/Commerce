import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from orders.models import Order, Payment
from .models import PaymentIntent

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_process(request, order_id):
    """
    Process payment for an order
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
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(order.total_amount * 100),  # Convert to cents
                            'product_data': {
                                'name': f'Order #{order.id}',
                                'description': f'Order #{order.id} from Our Store',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri(settings.PAYMENT_SUCCESS_URL),
                cancel_url=request.build_absolute_uri(settings.PAYMENT_CANCEL_URL),
                client_reference_id=str(order.id),
                customer_email=request.user.email,
            )
            
            # Create payment intent record
            PaymentIntent.objects.create(
                order=order,
                payment_intent_id=checkout_session.payment_intent,
                amount=order.total_amount,
                status='pending'
            )
            
            # Redirect to Stripe payment form
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
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
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the order
        order_id = int(session.get('client_reference_id'))
        order = Order.objects.get(id=order_id)
        
        # Update payment intent status
        payment_intent = PaymentIntent.objects.get(payment_intent_id=session.payment_intent)
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
            transaction_id=session.payment_intent,
            paid_at=timezone.now()
        )
    
    return HttpResponse(status=200)
