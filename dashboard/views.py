from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from store.models import Product
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
