from django.shortcuts import render
from store.models import Product, Category, Brand
from django.db.models import Count, Avg

def home(request):
    """
    Homepage view
    """
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
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'top_categories': top_categories,
        'top_brands': top_brands,
        'top_rated': top_rated,
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
