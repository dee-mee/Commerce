from decimal import Decimal
from django.conf import settings
from store.models import Product, ProductVariant

class Cart:
    """
    Shopping cart class that can work with both session-based and database-based carts
    """
    
    def __init__(self, request):
        """
        Initialize the cart
        """
        self.session = request.session
        self.user = request.user
        
        # Get cart from session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        # If no cart in session, create a new one
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            
        self.cart = cart
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database
        """
        product_ids = self.cart.keys()
        
        # Get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
            # Get variant if it exists
            if cart[str(product.id)].get('variant_id'):
                variant_id = cart[str(product.id)]['variant_id']
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    cart[str(product.id)]['variant'] = variant
                except ProductVariant.DoesNotExist:
                    cart[str(product.id)]['variant'] = None
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def add(self, product, quantity=1, override_quantity=False, variant_id=None):
        """
        Add a product to the cart or update its quantity
        """
        product_id = str(product.id)
        
        # If product not in cart, add it
        if product_id not in self.cart:
            # Get price based on variant if provided
            price = product.get_price()
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    if variant.price_override:
                        price = variant.price_override
                except ProductVariant.DoesNotExist:
                    variant_id = None
            
            self.cart[product_id] = {
                'quantity': 0, 
                'price': str(price),
                'variant_id': variant_id
            }
        
        # Update quantity
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def update(self, product_id, quantity):
        """
        Update quantity of a product
        """
        if str(product_id) in self.cart:
            self.cart[str(product_id)]['quantity'] = quantity
            self.save()
    
    def remove(self, product_id):
        """
        Remove a product from the cart
        """
        if str(product_id) in self.cart:
            del self.cart[str(product_id)]
            self.save()
    
    def clear(self):
        """
        Clear the cart
        """
        # Remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_subtotal(self):
        """
        Get the subtotal of all items in the cart
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
    
    def save(self):
        """
        Save the cart to the session
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        # Mark the session as modified
        self.session.modified = True
