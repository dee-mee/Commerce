from django.shortcuts import render
from django.utils import timezone
from store.models import Product, Category, Brand, FlashSale, FlashSaleItem
from django.db.models import Count, Avg

def home(request):
    """
    Homepage view
    """
    # Get current time for flash sales
    now = timezone.now()
    
    # Get active flash sales
    active_flash_sale = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by('end_time').first()
    
    # Get flash sale items if there's an active sale
    flash_sale_items = []
    if active_flash_sale:
        flash_sale_items = FlashSaleItem.objects.filter(
            flash_sale=active_flash_sale,
            stock_quantity__gt=0
        ).select_related('product')[:6]
    
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    
    # Get new arrivals
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    # Get top categories
    top_categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:6]
    
    # Get top brands
    top_brands = Brand.objects.filter(is_active=True).annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:6]
    
    # Get top rated products
    top_rated = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:4]
    
    context = {
        'active_flash_sale': active_flash_sale,
        'flash_sale_items': flash_sale_items,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'top_categories': top_categories,
        'top_brands': top_brands,
        'top_rated': top_rated,
        'current_time': now,
    }
    return render(request, 'core/home.html', context)

def about(request):
    """
    About page view
    """
    return render(request, 'core/about.html')

def contact(request):
    """
    Contact page view
    """
    return render(request, 'core/contact.html')

def faq(request):
    """
    FAQ page view
    """
    return render(request, 'core/faq.html')

def vendor_terms(request):
    """
    Vendor Terms and Conditions page view
    """
    return render(request, 'core/vendor_terms.html')
