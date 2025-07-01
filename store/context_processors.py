from .models import Category

def categories(request):
    """
    Add categories to the template context
    """
    return {
        'categories': Category.objects.filter(is_active=True)
    }
