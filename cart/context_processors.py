from .cart import Cart

def cart(request):
    """
    Context processor for cart to make it available in all templates
    """
    return {'cart': Cart(request)}
