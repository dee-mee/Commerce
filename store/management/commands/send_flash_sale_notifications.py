from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from store.models import FlashSale, FlashSaleNotification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send notifications for upcoming flash sales'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find flash sales that are about to start (within the next hour)
        upcoming_sales = FlashSale.objects.filter(
            is_active=True,
            start_time__gt=now,
            start_time__lte=now + timezone.timedelta(hours=1)
        )
        
        self.stdout.write(f"Found {upcoming_sales.count()} upcoming flash sales")
        
        # For each upcoming sale, find users who have subscribed but not been notified
        for sale in upcoming_sales:
            notifications = FlashSaleNotification.objects.filter(
                flash_sale=sale,
                is_notified=False
            )
            
            self.stdout.write(f"Sending {notifications.count()} notifications for '{sale.title}'")
            
            # Send email notifications
            for notification in notifications:
                try:
                    user = notification.user
                    
                    # Get the domain
                    domain = Site.objects.get_current().domain
                    
                    # Create the sale URL
                    sale_url = f"https://{domain}{reverse('store:flash_sale_detail', args=[sale.id])}"
                    
                    # Prepare email context
                    context = {
                        'user': user,
                        'sale': sale,
                        'sale_url': sale_url,
                        'minutes_until_start': int((sale.start_time - now).total_seconds() / 60)
                    }
                    
                    # Render email content
                    subject = f"🔥 Flash Sale Alert: {sale.title} starts soon!"
                    html_message = render_to_string('emails/flash_sale_notification.html', context)
                    plain_message = render_to_string('emails/flash_sale_notification.txt', context)
                    
                    # Send the email
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    
                    # Mark as notified
                    notification.is_notified = True
                    notification.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Notification sent to {user.email}"))
                    
                except Exception as e:
                    logger.error(f"Error sending notification to {user.email}: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"Error sending notification: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Flash sale notification process completed"))
