import random
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from store.models import Category, Brand, Product, ProductImage, FlashSale, FlashSaleItem
from accounts.models import VendorProfile
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to populate database with sample data...')
        
        # Create categories
        self.create_categories()
        
        # Create brands
        self.create_brands()
        
        # Create vendors
        self.create_vendors()
        
        # Create products
        self.create_products()
        
        # Create flash sales
        self.create_flash_sales()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
        
    def create_vendors(self):
        vendors = [
            {
                'username': 'techvendor',
                'email': 'tech@example.com',
                'password': 'password123',
                'store_name': 'Tech Haven',
                'description': 'Your one-stop shop for all tech needs',
            },
            {
                'username': 'fashionista',
                'email': 'fashion@example.com',
                'password': 'password123',
                'store_name': 'Fashion Forward',
                'description': 'Trendy clothing and accessories',
            },
            {
                'username': 'homegoods',
                'email': 'home@example.com',
                'password': 'password123',
                'store_name': 'Home Essentials',
                'description': 'Everything you need for your home',
            },
        ]
        
        created_count = 0
        for vendor_data in vendors:
            user, created = User.objects.get_or_create(
                username=vendor_data['username'],
                defaults={
                    'email': vendor_data['email'],
                    'is_vendor': True,
                }
            )
            
            if created:
                user.set_password(vendor_data['password'])
                user.save()
                created_count += 1
            
            # Create or update vendor profile
            VendorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'store_name': vendor_data['store_name'],
                    'description': vendor_data['description'],
                    'approved': True,
                }
            )
        
        self.stdout.write(f'Created {created_count} vendor accounts')
        self.vendor_profiles = list(VendorProfile.objects.all())
    
    def create_categories(self):
        categories = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen', 'description': 'Items for your home and kitchen'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books of all genres'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors', 'description': 'Sports equipment and outdoor gear'},
            {'name': 'Beauty & Personal Care', 'slug': 'beauty-personal-care', 'description': 'Beauty products and personal care items'},
            {'name': 'Toys & Games', 'slug': 'toys-games', 'description': 'Toys and games for all ages'},
            {'name': 'Automotive', 'slug': 'automotive', 'description': 'Automotive parts and accessories'},
            {'name': 'Health & Wellness', 'slug': 'health-wellness', 'description': 'Health and wellness products'},
            {'name': 'Pet Supplies', 'slug': 'pet-supplies', 'description': 'Supplies for your pets'},
        ]
        
        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'slug': category_data['slug'],
                    'description': category_data['description'],
                    'is_active': True
                }
            )
        
        self.stdout.write(f'Created {len(categories)} categories')
    
    def create_brands(self):
        brands = [
            {'name': 'Apple', 'slug': 'apple', 'description': 'Innovative technology products'},
            {'name': 'Samsung', 'slug': 'samsung', 'description': 'Electronics and appliances'},
            {'name': 'Nike', 'slug': 'nike', 'description': 'Athletic apparel and footwear'},
            {'name': 'Adidas', 'slug': 'adidas', 'description': 'Sports clothing and accessories'},
            {'name': 'Sony', 'slug': 'sony', 'description': 'Electronics and entertainment'},
            {'name': 'LG', 'slug': 'lg', 'description': 'Electronics and home appliances'},
            {'name': 'H&M', 'slug': 'hm', 'description': 'Fashion clothing for everyone'},
            {'name': 'Zara', 'slug': 'zara', 'description': 'Trendy fashion items'},
            {'name': 'IKEA', 'slug': 'ikea', 'description': 'Furniture and home accessories'},
            {'name': 'Philips', 'slug': 'philips', 'description': 'Electronics and personal care'},
            {'name': 'Logitech', 'slug': 'logitech', 'description': 'Computer peripherals and accessories'},
            {'name': 'Dell', 'slug': 'dell', 'description': 'Computers and related products'},
            {'name': 'HP', 'slug': 'hp', 'description': 'Computers and printers'},
            {'name': 'Canon', 'slug': 'canon', 'description': 'Cameras and imaging products'},
            {'name': 'Bosch', 'slug': 'bosch', 'description': 'Home appliances and power tools'},
        ]
        
        for brand_data in brands:
            Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'slug': brand_data['slug'],
                    'description': brand_data['description'],
                    'is_active': True
                }
            )
        
        self.stdout.write(f'Created {len(brands)} brands')
    
    def create_products(self):
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        
        if not categories or not brands or not hasattr(self, 'vendor_profiles') or not self.vendor_profiles:
            self.stdout.write(self.style.ERROR('No categories, brands, or vendors found. Please create them first.'))
            return
        
        products = [
            # Electronics
            {'name': 'Smartphone X Pro', 'description': 'Latest smartphone with advanced features', 'category': 'Electronics', 'brand': 'Apple', 'price': 999.99},
            {'name': 'Laptop Ultra', 'description': 'Powerful laptop for professionals', 'category': 'Electronics', 'brand': 'Dell', 'price': 1299.99},
            {'name': 'Wireless Earbuds', 'description': 'Premium wireless earbuds with noise cancellation', 'category': 'Electronics', 'brand': 'Sony', 'price': 149.99},
            {'name': 'Smart TV 55"', 'description': '4K Ultra HD Smart TV with HDR', 'category': 'Electronics', 'brand': 'Samsung', 'price': 699.99},
            {'name': 'Digital Camera', 'description': 'Professional digital camera with 24MP sensor', 'category': 'Electronics', 'brand': 'Canon', 'price': 799.99},
            {'name': 'Gaming Console', 'description': 'Next-gen gaming console with 1TB storage', 'category': 'Electronics', 'brand': 'Sony', 'price': 499.99},
            {'name': 'Bluetooth Speaker', 'description': 'Portable Bluetooth speaker with 20-hour battery life', 'category': 'Electronics', 'brand': 'LG', 'price': 79.99},
            {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse for productivity', 'category': 'Electronics', 'brand': 'Logitech', 'price': 49.99},
            {'name': 'Tablet Pro', 'description': '10-inch tablet with high-resolution display', 'category': 'Electronics', 'brand': 'Samsung', 'price': 349.99},
            {'name': 'Smart Watch', 'description': 'Fitness tracker and smartwatch with heart rate monitor', 'category': 'Electronics', 'brand': 'Apple', 'price': 299.99},
            
            # Clothing
            {'name': 'Men\'s Running Shoes', 'description': 'Lightweight running shoes for men', 'category': 'Clothing', 'brand': 'Nike', 'price': 89.99},
            {'name': 'Women\'s Yoga Pants', 'description': 'Comfortable yoga pants for women', 'category': 'Clothing', 'brand': 'Adidas', 'price': 59.99},
            {'name': 'Men\'s T-Shirt', 'description': 'Cotton t-shirt for casual wear', 'category': 'Clothing', 'brand': 'H&M', 'price': 19.99},
            {'name': 'Women\'s Dress', 'description': 'Elegant dress for special occasions', 'category': 'Clothing', 'brand': 'Zara', 'price': 79.99},
            {'name': 'Men\'s Jeans', 'description': 'Classic jeans for everyday wear', 'category': 'Clothing', 'brand': 'H&M', 'price': 49.99},
            {'name': 'Women\'s Blouse', 'description': 'Stylish blouse for work or casual wear', 'category': 'Clothing', 'brand': 'Zara', 'price': 39.99},
            {'name': 'Men\'s Jacket', 'description': 'Waterproof jacket for outdoor activities', 'category': 'Clothing', 'brand': 'Nike', 'price': 129.99},
            {'name': 'Women\'s Sneakers', 'description': 'Comfortable sneakers for everyday use', 'category': 'Clothing', 'brand': 'Adidas', 'price': 69.99},
            
            # Home & Kitchen
            {'name': 'Coffee Maker', 'description': 'Programmable coffee maker with 12-cup capacity', 'category': 'Home & Kitchen', 'brand': 'Philips', 'price': 89.99},
            {'name': 'Blender', 'description': 'High-performance blender for smoothies and more', 'category': 'Home & Kitchen', 'brand': 'Bosch', 'price': 69.99},
            {'name': 'Toaster', 'description': '2-slice toaster with multiple settings', 'category': 'Home & Kitchen', 'brand': 'Philips', 'price': 39.99},
            {'name': 'Microwave Oven', 'description': 'Countertop microwave with 1000W power', 'category': 'Home & Kitchen', 'brand': 'LG', 'price': 119.99},
            {'name': 'Dining Table Set', 'description': '6-person dining table set with chairs', 'category': 'Home & Kitchen', 'brand': 'IKEA', 'price': 399.99},
            {'name': 'Sofa', 'description': '3-seater sofa with comfortable cushions', 'category': 'Home & Kitchen', 'brand': 'IKEA', 'price': 599.99},
            
            # Books
            {'name': 'Fiction Bestseller', 'description': 'Latest bestselling fiction novel', 'category': 'Books', 'brand': None, 'price': 24.99},
            {'name': 'Cookbook', 'description': 'Collection of gourmet recipes', 'category': 'Books', 'brand': None, 'price': 29.99},
            {'name': 'Self-Help Book', 'description': 'Guide to personal development', 'category': 'Books', 'brand': None, 'price': 19.99},
            {'name': 'Children\'s Book', 'description': 'Illustrated book for children', 'category': 'Books', 'brand': None, 'price': 14.99},
            
            # Sports & Outdoors
            {'name': 'Yoga Mat', 'description': 'Non-slip yoga mat for home workouts', 'category': 'Sports & Outdoors', 'brand': 'Adidas', 'price': 29.99},
            {'name': 'Dumbbells Set', 'description': 'Adjustable dumbbells for strength training', 'category': 'Sports & Outdoors', 'brand': None, 'price': 149.99},
            {'name': 'Tennis Racket', 'description': 'Professional tennis racket', 'category': 'Sports & Outdoors', 'brand': None, 'price': 89.99},
            {'name': 'Basketball', 'description': 'Official size basketball', 'category': 'Sports & Outdoors', 'brand': 'Nike', 'price': 29.99},
            {'name': 'Camping Tent', 'description': '4-person camping tent for outdoor adventures', 'category': 'Sports & Outdoors', 'brand': None, 'price': 199.99},
            
            # Beauty & Personal Care
            {'name': 'Facial Cleanser', 'description': 'Gentle facial cleanser for all skin types', 'category': 'Beauty & Personal Care', 'brand': None, 'price': 14.99},
            {'name': 'Shampoo', 'description': 'Moisturizing shampoo for dry hair', 'category': 'Beauty & Personal Care', 'brand': None, 'price': 9.99},
            {'name': 'Perfume', 'description': 'Luxury perfume with floral notes', 'category': 'Beauty & Personal Care', 'brand': None, 'price': 79.99},
            {'name': 'Electric Toothbrush', 'description': 'Rechargeable electric toothbrush', 'category': 'Beauty & Personal Care', 'brand': 'Philips', 'price': 49.99},
            {'name': 'Hair Dryer', 'description': 'Professional hair dryer with multiple settings', 'category': 'Beauty & Personal Care', 'brand': 'Philips', 'price': 59.99},
            
            # Toys & Games
            {'name': 'Board Game', 'description': 'Family board game for all ages', 'category': 'Toys & Games', 'brand': None, 'price': 34.99},
            {'name': 'Action Figure', 'description': 'Collectible action figure', 'category': 'Toys & Games', 'brand': None, 'price': 19.99},
            {'name': 'Puzzle', 'description': '1000-piece jigsaw puzzle', 'category': 'Toys & Games', 'brand': None, 'price': 24.99},
            {'name': 'Remote Control Car', 'description': 'High-speed remote control car', 'category': 'Toys & Games', 'brand': None, 'price': 49.99},
            
            # Automotive
            {'name': 'Car Vacuum Cleaner', 'description': 'Portable vacuum cleaner for cars', 'category': 'Automotive', 'brand': None, 'price': 39.99},
            {'name': 'Car Phone Mount', 'description': 'Universal phone mount for cars', 'category': 'Automotive', 'brand': None, 'price': 19.99},
            {'name': 'Car Seat Cover', 'description': 'Durable seat covers for cars', 'category': 'Automotive', 'brand': None, 'price': 49.99},
            
            # Health & Wellness
            {'name': 'Vitamin Supplements', 'description': 'Daily multivitamin supplements', 'category': 'Health & Wellness', 'brand': None, 'price': 29.99},
            {'name': 'Digital Scale', 'description': 'Bathroom scale with body composition analysis', 'category': 'Health & Wellness', 'brand': None, 'price': 49.99},
            {'name': 'Blood Pressure Monitor', 'description': 'Digital blood pressure monitor for home use', 'category': 'Health & Wellness', 'brand': 'Philips', 'price': 69.99},
            
            # Pet Supplies
            {'name': 'Dog Food', 'description': 'Premium dog food for adult dogs', 'category': 'Pet Supplies', 'brand': None, 'price': 39.99},
            {'name': 'Cat Litter Box', 'description': 'Self-cleaning cat litter box', 'category': 'Pet Supplies', 'brand': None, 'price': 89.99},
            {'name': 'Pet Bed', 'description': 'Comfortable bed for dogs and cats', 'category': 'Pet Supplies', 'brand': None, 'price': 49.99},
            {'name': 'Pet Toys', 'description': 'Set of interactive toys for pets', 'category': 'Pet Supplies', 'brand': None, 'price': 19.99},
        ]
        
        created_count = 0
        for product_data in products:
            category = next((c for c in categories if c.name == product_data['category']), None)
            
            brand = None
            if product_data['brand']:
                brand = next((b for b in brands if b.name == product_data['brand']), None)
            else:
                # If no brand is specified, use a generic brand
                brand = next((b for b in brands if b.name == 'Generic'), None)
                if not brand:
                    # Create a generic brand if it doesn't exist
                    brand = Brand.objects.create(
                        name='Generic',
                        slug='generic',
                        description='Generic brand for unbranded products',
                        is_active=True
                    )
                    brands.append(brand)
            
            if not category:
                self.stdout.write(f"Category '{product_data['category']}' not found, skipping product '{product_data['name']}'")
                continue
                
            if not brand:
                self.stdout.write(f"Brand not found for product '{product_data['name']}', skipping")
                continue
            
            # Assign appropriate vendor based on category
            if product_data['category'] == 'Electronics':
                vendor = next((v for v in self.vendor_profiles if v.store_name == 'Tech Haven'), self.vendor_profiles[0])
            elif product_data['category'] == 'Clothing':
                vendor = next((v for v in self.vendor_profiles if v.store_name == 'Fashion Forward'), self.vendor_profiles[0])
            elif product_data['category'] == 'Home & Kitchen':
                vendor = next((v for v in self.vendor_profiles if v.store_name == 'Home Essentials'), self.vendor_profiles[0])
            else:
                # Randomly assign a vendor for other categories
                vendor = random.choice(self.vendor_profiles)
            
            # Generate a unique SKU
            sku = f"{category.name[:3].upper()}-{product_data['name'][:3].upper()}-{random.randint(1000, 9999)}"
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'category': category,
                    'brand': brand,
                    'vendor': vendor,
                    'price': product_data['price'],
                    'stock': random.randint(10, 100),
                    'sku': sku,
                    'is_active': True,
                    'is_featured': random.choice([True, False]),
                    'slug': product_data['name'].lower().replace(' ', '-').replace("'", ''),
                }
            )
            
            if created:
                created_count += 1
                # Create a dummy product image
                ProductImage.objects.create(
                    product=product,
                    image='products/default.jpg',
                    is_primary=True
                )
        
        self.stdout.write(f'Created {created_count} products')
    
    def create_flash_sales(self):
        products = list(Product.objects.all())
        
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please create them first.'))
            return
        
        now = timezone.now()
        
        # Create active flash sale (happening now)
        active_sale, created = FlashSale.objects.get_or_create(
            title='Summer Flash Sale',
            defaults={
                'description': 'Hot deals for summer! Limited time only.',
                'start_time': now - datetime.timedelta(hours=2),
                'end_time': now + datetime.timedelta(hours=22),
                'is_active': True,
            }
        )
        
        # Create upcoming flash sale (starting tomorrow)
        tomorrow = now + datetime.timedelta(days=1)
        upcoming_sale, created = FlashSale.objects.get_or_create(
            title='Weekend Special',
            defaults={
                'description': 'Incredible deals for the weekend!',
                'start_time': tomorrow,
                'end_time': tomorrow + datetime.timedelta(days=2),
                'is_active': True,
            }
        )
        
        # Create another upcoming flash sale (starting in 3 days)
        next_week = now + datetime.timedelta(days=3)
        next_sale, created = FlashSale.objects.get_or_create(
            title='Tech Bonanza',
            defaults={
                'description': 'Massive discounts on all tech products!',
                'start_time': next_week,
                'end_time': next_week + datetime.timedelta(days=1),
                'is_active': True,
            }
        )
        
        # Add products to active flash sale
        electronics_products = [p for p in products if p.category.name == 'Electronics']
        clothing_products = [p for p in products if p.category.name == 'Clothing']
        home_products = [p for p in products if p.category.name == 'Home & Kitchen']
        
        with transaction.atomic():
            # Add electronics products to active sale
            for product in random.sample(electronics_products, min(5, len(electronics_products))):
                stock_quantity = random.randint(5, 20)
                discount_percentage = 25
                flash_sale_price = product.price * Decimal('0.75')  # 25% off
                FlashSaleItem.objects.get_or_create(
                    flash_sale=active_sale,
                    product=product,
                    defaults={
                        'discount_percentage': discount_percentage,
                        'flash_sale_price': flash_sale_price,
                        'original_price': product.price,
                        'stock_quantity': stock_quantity,
                        'initial_stock_quantity': stock_quantity,
                    }
                )
            
            # Add clothing products to upcoming sale
            for product in random.sample(clothing_products, min(5, len(clothing_products))):
                stock_quantity = random.randint(10, 30)
                discount_percentage = 30
                flash_sale_price = product.price * Decimal('0.7')  # 30% off
                FlashSaleItem.objects.get_or_create(
                    flash_sale=upcoming_sale,
                    product=product,
                    defaults={
                        'discount_percentage': discount_percentage,
                        'flash_sale_price': flash_sale_price,
                        'original_price': product.price,
                        'stock_quantity': stock_quantity,
                        'initial_stock_quantity': stock_quantity,
                    }
                )
            
            # Add home products to next week's sale
            for product in random.sample(home_products, min(3, len(home_products))):
                stock_quantity = random.randint(15, 25)
                discount_percentage = 40
                flash_sale_price = product.price * 0.6  # 40% off
                FlashSaleItem.objects.get_or_create(
                    flash_sale=next_sale,
                    product=product,
                    defaults={
                        'discount_percentage': discount_percentage,
                        'flash_sale_price': flash_sale_price,
                        'original_price': product.price,
                        'stock_quantity': stock_quantity,
                        'initial_stock_quantity': stock_quantity,
                    }
                )
            
            # Add some electronics to next week's sale too (it's a tech bonanza after all)
            for product in random.sample(electronics_products, min(7, len(electronics_products))):
                stock_quantity = random.randint(15, 25)
                discount_percentage = 40
                flash_sale_price = product.price * 0.6  # 40% off
                FlashSaleItem.objects.get_or_create(
                    flash_sale=next_sale,
                    product=product,
                    defaults={
                        'discount_percentage': discount_percentage,
                        'flash_sale_price': flash_sale_price,
                        'original_price': product.price,
                        'stock_quantity': stock_quantity,
                        'initial_stock_quantity': stock_quantity,
                    }
                )
        
        self.stdout.write(f'Created 3 flash sales with products')
