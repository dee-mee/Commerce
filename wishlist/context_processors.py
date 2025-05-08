from .models import Wishlist

def wishlist_count(request):
    """
    Context processor that adds the wishlist count to the context.
    """
    count = 0
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            count = wishlist.products.count()
        except Wishlist.DoesNotExist:
            pass
    
    return {'wishlist_count': count}
