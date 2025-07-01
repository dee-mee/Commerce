from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from datetime import timedelta

from orders.models import Order
from store.models import Product, FlashSale, FlashSaleItem, FlashSaleNotification
from accounts.models import User

@staff_member_required
def dashboard_home(request):
    # Get basic statistics for the dashboard
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Get recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    # Get sales data for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_sales = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'monthly_sales': monthly_sales,
    }
    
    return render(request, 'dashboard/dashboard_home.html', context)

@staff_member_required
def sales_analytics(request):
    # Get sales data for different time periods
    today = timezone.now().date()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    start_of_week = start_of_day - timedelta(days=today.weekday())
    start_of_month = timezone.make_aware(timezone.datetime(today.year, today.month, 1))
    
    # Calculate sales for different periods
    daily_sales = Order.objects.filter(
        created_at__gte=start_of_day,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    weekly_sales = Order.objects.filter(
        created_at__gte=start_of_week,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    monthly_sales = Order.objects.filter(
        created_at__gte=start_of_month,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
    }
    
    return render(request, 'dashboard/sales_analytics.html', context)

@staff_member_required
def product_management(request):
    # Get all products with their stats
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products,
    }
    
    return render(request, 'dashboard/product_management.html', context)

@staff_member_required
def order_management(request):
    # Get all orders
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'dashboard/order_management.html', context)

@staff_member_required
def customer_management(request):
    # Get all customers (non-staff users)
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'dashboard/customer_management.html', context)

@staff_member_required
def flash_sales_management(request):
    """
    Dashboard view for managing flash sales
    """
    now = timezone.now()
    
    # Get active, upcoming, and past flash sales
    active_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by('end_time')
    
    upcoming_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__gt=now
    ).order_by('start_time')
    
    past_sales = FlashSale.objects.filter(
        end_time__lt=now
    ).order_by('-end_time')[:10]  # Show only the 10 most recent past sales
    
    # Calculate performance metrics for active sales
    for sale in active_sales:
        # Get all items in this sale
        sale_items = FlashSaleItem.objects.filter(flash_sale=sale)
        
        # Calculate total items sold
        total_sold = sum([item.initial_stock_quantity - item.stock_quantity for item in sale_items])
        sale.total_sold = total_sold
        
        # Calculate total revenue
        sale.total_revenue = sum([item.flash_sale_price * (item.initial_stock_quantity - item.stock_quantity) for item in sale_items])
        
        # Calculate percentage sold
        total_initial_stock = sum([item.initial_stock_quantity for item in sale_items])
        sale.percentage_sold = (total_sold / total_initial_stock * 100) if total_initial_stock > 0 else 0
        
        # Calculate time remaining
        sale.time_remaining = sale.end_time - now
        
        # Get subscriber count
        sale.subscriber_count = FlashSaleNotification.objects.filter(flash_sale=sale).count()
    
    context = {
        'active_sales': active_sales,
        'upcoming_sales': upcoming_sales,
        'past_sales': past_sales,
        'current_time': now,
    }
    
    return render(request, 'dashboard/flash_sales_management.html', context)

@staff_member_required
def flash_sale_detail_admin(request, sale_id):
    """
    Dashboard view for managing a specific flash sale
    """
    sale = get_object_or_404(FlashSale, id=sale_id)
    now = timezone.now()
    
    # Check if the sale is active
    is_active = sale.start_time <= now <= sale.end_time
    
    # Get all items in this flash sale with performance metrics
    sale_items = FlashSaleItem.objects.filter(flash_sale=sale).select_related('product')
    
    for item in sale_items:
        # Calculate items sold
        item.sold_count = item.initial_stock_quantity - item.stock_quantity
        
        # Calculate revenue
        item.revenue = item.flash_sale_price * item.sold_count
        
        # Calculate percentage sold
        item.percentage_sold = (item.sold_count / item.initial_stock_quantity * 100) if item.initial_stock_quantity > 0 else 0
    
    # Get subscriber count
    subscriber_count = FlashSaleNotification.objects.filter(flash_sale=sale).count()
    
    context = {
        'flash_sale': sale,
        'sale_items': sale_items,
        'is_active': is_active,
        'subscriber_count': subscriber_count,
        'current_time': now,
    }
    
    return render(request, 'dashboard/flash_sale_detail_admin.html', context)

@staff_member_required
def update_flash_sale_stock(request, item_id):
    """
    API endpoint to update flash sale item stock
    """
    if request.method == 'POST':
        try:
            item = get_object_or_404(FlashSaleItem, id=item_id)
            new_stock = int(request.POST.get('stock_quantity', 0))
            
            # Validate the new stock value
            if new_stock < 0:
                return JsonResponse({'error': 'Stock quantity cannot be negative'}, status=400)
            
            # Update the stock
            item.stock_quantity = new_stock
            item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Stock updated to {new_stock}',
                'stock_quantity': new_stock,
                'remaining_percentage': item.get_remaining_percentage()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
