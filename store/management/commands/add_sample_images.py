import os
from django.core.management.base import BaseCommand
from django.core.files import File
from store.models import Product, ProductImage
import requests
from io import BytesIO
import tempfile

class Command(BaseCommand):
    help = 'Add sample images to products'

    def download_image(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None

    def handle(self, *args, **kwargs):
        # Sample image URLs for different product categories
        image_urls = {
            'Wireless Headphones': [
                'https://example.com/headphones1.jpg',
                'https://example.com/headphones2.jpg',
            ],
            'Smart Watch': [
                'https://example.com/smartwatch1.jpg',
                'https://example.com/smartwatch2.jpg',
            ],
            'Denim Jacket': [
                'https://example.com/jacket1.jpg',
                'https://example.com/jacket2.jpg',
            ],
            'Cotton T-Shirt': [
                'https://example.com/tshirt1.jpg',
                'https://example.com/tshirt2.jpg',
            ],
            'Modern Coffee Table': [
                'https://example.com/table1.jpg',
                'https://example.com/table2.jpg',
            ],
            'Desk Lamp': [
                'https://example.com/lamp1.jpg',
                'https://example.com/lamp2.jpg',
            ],
            'Python Programming Guide': [
                'https://example.com/pythonbook1.jpg',
                'https://example.com/pythonbook2.jpg',
            ],
            'Web Development Basics': [
                'https://example.com/webbook1.jpg',
                'https://example.com/webbook2.jpg',
            ],
        }

        # For now, let's create placeholder images since we can't download from example.com
        for product_name, urls in image_urls.items():
            try:
                product = Product.objects.get(name=product_name)
                
                # Create a temporary image file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    # Create a simple colored rectangle (you would normally download real images)
                    from PIL import Image
                    img = Image.new('RGB', (800, 800), color='white')
                    img.save(tmp.name, 'JPEG')
                    
                    # Create primary product image
                    with open(tmp.name, 'rb') as img_file:
                        product_image = ProductImage.objects.create(
                            product=product,
                            is_primary=True,
                            alt_text=f"{product_name} primary image"
                        )
                        product_image.image.save(
                            f"{product_name.lower().replace(' ', '_')}_1.jpg",
                            File(img_file),
                            save=True
                        )
                    
                    # Create secondary product image
                    with open(tmp.name, 'rb') as img_file:
                        product_image = ProductImage.objects.create(
                            product=product,
                            is_primary=False,
                            alt_text=f"{product_name} secondary image"
                        )
                        product_image.image.save(
                            f"{product_name.lower().replace(' ', '_')}_2.jpg",
                            File(img_file),
                            save=True
                        )
                
                self.stdout.write(self.style.SUCCESS(f'Added images for product: {product_name}'))
                
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product not found: {product_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding images for {product_name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully added sample images'))
