from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Product, Category, Brand, Review, ReviewImage, FlashSale, FlashSaleItem
from .forms import ReviewForm, ReviewImageFormSet
from wishlist.models import Wishlist

def product_list(request):
    """
    List all products with filtering options
    """
    products = Product.objects.filter(is_active=True).annotate(avg_rating=Avg('reviews__rating'))
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filter by brand
    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort', 'default')
    if sort == 'price' or sort == 'price_low':
        products = products.order_by('price')
    elif sort == '-price' or sort == 'price_high':
        products = products.order_by('-price')
    elif sort == '-created_at' or sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == '-avg_rating' or sort == 'rating':
        products = products.order_by('-avg_rating')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories and brands for filters
    categories = Category.objects.filter(is_active=True, parent=None)
    brands = Brand.objects.filter(is_active=True)
    
    # Get user's wishlist products if authenticated
    wishlist_products = []
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'current_brands': brand_slugs,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/product_list_wishlist.html', context)

def product_detail(request, slug):
    """
    Display product details
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get related products
    related_products = Product.objects.filter(
        Q(category=product.category) | Q(brand=product.brand)
    ).exclude(id=product.id).distinct()[:4]
    
    # Get reviews
    reviews = product.reviews.filter(approved=True)
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            in_wishlist = product in wishlist.products.all()
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail_wishlist.html', context)

def category_detail(request, slug):
    """
    Display products in a specific category
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all products in this category and its subcategories
    subcategories = category.children.filter(is_active=True)
    products = Product.objects.filter(
        Q(category=category) | Q(category__in=subcategories),
        is_active=True
    )
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj,
    }
    return render(request, 'store/category_detail.html', context)

def brand_detail(request, slug):
    """
    Display products from a specific brand
    """
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(brand=brand, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'page_obj': page_obj,
    }
    return render(request, 'store/brand_detail.html', context)

def search_products(request):
    """
    Search products by keyword
    """
    query = request.GET.get('q', '')
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(meta_keywords__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query),
            is_active=True
        ).distinct()
    else:
        products = Product.objects.none()
    
    # Filter by category
    current_category = request.GET.get('category')
    if current_category and current_category != 'all':
        products = products.filter(category_id=current_category)
    
    # Filter by brand
    current_brand = request.GET.get('brand')
    if current_brand and current_brand != 'all':
        products = products.filter(brand_id=current_brand)
    
    # Filter by price range
    current_min_price = request.GET.get('min_price')
    current_max_price = request.GET.get('max_price')
    if current_min_price:
        products = products.filter(price__gte=current_min_price)
    if current_max_price:
        products = products.filter(price__lte=current_max_price)
    
    # Sorting
    current_sort = request.GET.get('sort', 'relevance')
    if current_sort == 'price_low':
        products = products.order_by('price')
    elif current_sort == 'price_high':
        products = products.order_by('-price')
    elif current_sort == 'newest':
        products = products.order_by('-created_at')
    elif current_sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories and brands for filtering sidebar
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
        'current_brand': current_brand,
        'current_min_price': current_min_price,
        'current_max_price': current_max_price,
        'current_sort': current_sort,
    }
    return render(request, 'store/search_results.html', context)

@login_required
def add_review(request, product_id):
    """
    Add a review to a product
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product')
        return redirect('store:product_detail', slug=product.slug)
    
    # Check if user has purchased the product
    from orders.models import OrderItem
    has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
    
    # Allow admins to review without purchase
    if not has_purchased and not request.user.is_staff:
        messages.warning(request, 'You can only review products you have purchased')
        return redirect('store:product_detail', slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        formset = ReviewImageFormSet(request.POST, request.FILES, prefix='images')
        
        if form.is_valid() and formset.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Save review images
            for image_form in formset:
                if image_form.cleaned_data.get('image'):
                    image = image_form.save(commit=False)
                    image.review = review
                    image.save()
            
            messages.success(request, 'Your review has been submitted')
            return redirect('store:product_detail', slug=product.slug)
    else:
        form = ReviewForm()
        formset = ReviewImageFormSet(prefix='images')
    
    context = {
        'form': form,
        'formset': formset,
        'product': product,
    }
    return render(request, 'store/add_review.html', context)


def flash_sale_list(request):
    """
    Display all active flash sales
    """
    now = timezone.now()
    
    # Get all ongoing flash sales
    flash_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by('end_time')
    
    # Get upcoming flash sales
    upcoming_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__gt=now
    ).order_by('start_time')[:5]  # Show only next 5 upcoming sales
    
    context = {
        'flash_sales': flash_sales,
        'upcoming_sales': upcoming_sales,
        'current_time': now,
    }
    return render(request, 'store/flash_sale_list.html', context)


def flash_sale_detail(request, sale_id):
    """
    Display products in a specific flash sale
    """
    flash_sale = get_object_or_404(FlashSale, id=sale_id, is_active=True)
    now = timezone.now()
    
    # Check if the sale is active
    is_active = flash_sale.start_time <= now <= flash_sale.end_time
    
    # Get all products in this flash sale
    sale_items = flash_sale.items.all().select_related('product')
    
    # Get user's wishlist products if authenticated
    wishlist_products = []
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'flash_sale': flash_sale,
        'sale_items': sale_items,
        'is_active': is_active,
        'wishlist_products': wishlist_products,
        'current_time': now,
    }
    return render(request, 'store/flash_sale_detail.html', context)
