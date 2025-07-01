import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth import get_user_model
from store.models import Category, Brand, Product, ProductImage, VendorProfile
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Add sample products to the database'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create a vendor if not exists
        vendor_user, _ = User.objects.get_or_create(
            username='vendor1',
            email='vendor1@example.com',
            defaults={'is_active': True}
        )
        vendor_user.set_password('vendor123')
        vendor_user.save()

        vendor_profile, _ = VendorProfile.objects.get_or_create(
            user=vendor_user,
            defaults={
                'store_name': 'Sample Vendor',
                'description': 'A sample vendor for demo purposes',
            }
        )

        # Create categories
        categories = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and accessories',
            },
            {
                'name': 'Fashion',
                'description': 'Clothing, shoes, and accessories',
            },
            {
                'name': 'Home & Living',
                'description': 'Furniture, decor, and home accessories',
            },
            {
                'name': 'Books',
                'description': 'Physical and digital books',
            },
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create brands
        brands = [
            {
                'name': 'TechPro',
                'description': 'High-quality electronics',
            },
            {
                'name': 'Fashionista',
                'description': 'Trendy fashion brands',
            },
            {
                'name': 'HomeStyle',
                'description': 'Modern home decor',
            },
            {
                'name': 'BookMaster',
                'description': 'Premier book publisher',
            },
        ]

        for brand_data in brands:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'description': brand_data['description'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created brand: {brand.name}'))

        # Create products
        products = [
            {
                'name': 'Wireless Headphones',
                'category': 'Electronics',
                'brand': 'TechPro',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': Decimal('99.99'),
                'sale_price': Decimal('79.99'),
                'stock': 50,
            },
            {
                'name': 'Smart Watch',
                'category': 'Electronics',
                'brand': 'TechPro',
                'description': 'Smart watch with health monitoring features',
                'price': Decimal('199.99'),
                'stock': 30,
            },
            {
                'name': 'Denim Jacket',
                'category': 'Fashion',
                'brand': 'Fashionista',
                'description': 'Classic denim jacket with modern styling',
                'price': Decimal('79.99'),
                'sale_price': Decimal('59.99'),
                'stock': 100,
            },
            {
                'name': 'Cotton T-Shirt',
                'category': 'Fashion',
                'brand': 'Fashionista',
                'description': 'Comfortable 100% cotton t-shirt',
                'price': Decimal('29.99'),
                'stock': 200,
            },
            {
                'name': 'Modern Coffee Table',
                'category': 'Home & Living',
                'brand': 'HomeStyle',
                'description': 'Stylish coffee table with storage',
                'price': Decimal('299.99'),
                'sale_price': Decimal('249.99'),
                'stock': 10,
            },
            {
                'name': 'Desk Lamp',
                'category': 'Home & Living',
                'brand': 'HomeStyle',
                'description': 'LED desk lamp with adjustable brightness',
                'price': Decimal('49.99'),
                'stock': 75,
            },
            {
                'name': 'Python Programming Guide',
                'category': 'Books',
                'brand': 'BookMaster',
                'description': 'Comprehensive guide to Python programming',
                'price': Decimal('39.99'),
                'stock': 150,
            },
            {
                'name': 'Web Development Basics',
                'category': 'Books',
                'brand': 'BookMaster',
                'description': 'Learn the basics of web development',
                'price': Decimal('34.99'),
                'sale_price': Decimal('29.99'),
                'stock': 100,
            },
        ]

        for product_data in products:
            category = Category.objects.get(name=product_data['category'])
            brand = Brand.objects.get(name=product_data['brand'])
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'brand': brand,
                    'vendor': vendor_profile,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'sale_price': product_data.get('sale_price'),
                    'stock': product_data['stock'],
                    'sku': f'SKU{random.randint(10000, 99999)}',
                    'is_featured': random.choice([True, False]),
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully added sample products'))
