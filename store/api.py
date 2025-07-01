from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from .models import FlashSaleItem, FlashSale, FlashSaleNotification

def get_flash_sale_stock(request):
    """
    API endpoint to get real-time stock information for flash sale items
    """
    if request.method == 'GET':
        sale_id = request.GET.get('sale_id')
        if not sale_id:
            return JsonResponse({'error': 'Sale ID is required'}, status=400)
        
        # Get all items for this sale with their current stock
        items = FlashSaleItem.objects.filter(flash_sale_id=sale_id)
        
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'product_id': item.product.id,
                'stock_quantity': item.stock_quantity,
                'initial_stock_quantity': item.initial_stock_quantity,
                'remaining_percentage': item.get_remaining_percentage(),
                'sold_out': item.stock_quantity <= 0
            })
        
        return JsonResponse({
            'success': True,
            'items': items_data,
            'timestamp': timezone.now().timestamp()
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@require_POST
def toggle_flash_sale_notification(request):
    """
    API endpoint to subscribe/unsubscribe to flash sale notifications
    """
    try:
        data = json.loads(request.body)
        sale_id = data.get('sale_id')
        action = data.get('action')  # 'subscribe' or 'unsubscribe'
        
        if not sale_id or not action:
            return JsonResponse({'error': 'Sale ID and action are required'}, status=400)
        
        flash_sale = get_object_or_404(FlashSale, id=sale_id)
        
        # Check if the user is already subscribed
        notification, created = FlashSaleNotification.objects.get_or_create(
            user=request.user,
            flash_sale=flash_sale
        )
        
        if action == 'subscribe':
            # User wants to subscribe
            if created:
                message = 'You will be notified when this flash sale starts'
            else:
                message = 'You are already subscribed to this flash sale'
                
            status = 'subscribed'
            
        elif action == 'unsubscribe':
            # User wants to unsubscribe
            if not created:
                notification.delete()
                message = 'You have been unsubscribed from this flash sale'
                status = 'unsubscribed'
            else:
                # This shouldn't happen, but just in case
                notification.delete()
                message = 'You were not subscribed to this flash sale'
                status = 'unsubscribed'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({
            'success': True,
            'status': status,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
