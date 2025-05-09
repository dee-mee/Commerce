from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from accounts.models import User, VendorProfile

class Category(models.Model):
    """
    Product category model
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Brand(models.Model):
    """
    Product brand model
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand_logos', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:brand_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    """
    Product model
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    meta_keywords = models.CharField(max_length=255, blank=True, help_text='Comma separated keywords for SEO')
    meta_description = models.TextField(blank=True, help_text='Content for meta description tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])
    
    def get_price(self):
        return self.sale_price if self.sale_price else self.price
    
    def is_on_sale(self):
        return self.sale_price is not None
    
    def get_discount_percentage(self):
        if self.is_on_sale():
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_avg_rating(self):
        """
        Calculate the average rating for this product
        Returns an integer from 0-5
        """
        reviews = self.reviews.filter(approved=True)
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count())
        return 0

class ProductImage(models.Model):
    """
    Product image model
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # If this is the primary image, set all other product images to not primary
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    """
    Product variant model (e.g., size, color)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Size", "Color"
    value = models.CharField(max_length=100)  # e.g., "Large", "Red"
    price_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_override = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = ('product', 'name', 'value')
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    def get_price(self):
        if self.price_override:
            return self.price_override
        return self.product.get_price()
    
    def get_stock(self):
        if self.stock_override is not None:
            return self.stock_override
        return self.product.stock

class Review(models.Model):
    """
    Product review model
    """
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"

class ReviewImage(models.Model):
    """
    Images for product reviews
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images')
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
    
    def __str__(self):
        return f"Image for {self.review}"


class FlashSale(models.Model):
    """
    Flash Sale model for time-limited product promotions
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Flash Sale'
        verbose_name_plural = 'Flash Sales'
        ordering = ('-start_time',)
    
    def __str__(self):
        return self.title
    
    def is_ongoing(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    def time_left(self):
        if not self.is_ongoing():
            return None
        
        now = timezone.now()
        time_remaining = self.end_time - now
        return time_remaining
    
    def time_left_display(self):
        time_remaining = self.time_left()
        if not time_remaining:
            return "Expired"
        
        seconds = time_remaining.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}h : {minutes:02d}m : {secs:02d}s"


class FlashSaleItem(models.Model):
    """
    Products included in a flash sale with special pricing
    """
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_sale_items')
    discount_percentage = models.PositiveIntegerField(help_text='Discount percentage (e.g., 20 for 20% off)')
    flash_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    initial_stock_quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Flash Sale Item'
        verbose_name_plural = 'Flash Sale Items'
        unique_together = ('flash_sale', 'product')
    
    def __str__(self):
        return f"{self.product.name} in {self.flash_sale.title}"
    
    def save(self, *args, **kwargs):
        # Calculate flash sale price if not provided
        if not self.flash_sale_price and self.product and self.discount_percentage:
            original_price = self.product.get_price()
            self.original_price = original_price
            self.flash_sale_price = original_price * (1 - self.discount_percentage / 100)
        
        # Set initial stock quantity if not provided
        if not self.initial_stock_quantity and self.stock_quantity:
            self.initial_stock_quantity = self.stock_quantity
            
        super().save(*args, **kwargs)
    
    def get_remaining_percentage(self):
        if self.initial_stock_quantity == 0:
            return 0
        return int((self.stock_quantity / self.initial_stock_quantity) * 100)
    
    def items_left(self):
        return self.stock_quantity


class FlashSaleNotification(models.Model):
    """
    Model for users to subscribe to flash sale notifications
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flash_sale_notifications')
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE, related_name='notifications')
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Flash Sale Notification'
        verbose_name_plural = 'Flash Sale Notifications'
        unique_together = ('user', 'flash_sale')
    
    def __str__(self):
        return f"{self.user.username}'s notification for {self.flash_sale.title}"
