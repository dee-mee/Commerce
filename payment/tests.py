from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order, PaymentMethod
from decimal import Decimal

class PaymentTests(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create payment methods
        self.credit_card = PaymentMethod.objects.create(
            name='credit_card',
            description='Pay with Credit Card',
            is_active=True
        )
        
        # Create a test order
        self.order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone='1234567890',
            address_line='123 Test St',
            city='Test City',
            state='Test State',
            country='US',
            postal_code='12345',
            total_amount=Decimal('100.00'),
            shipping_amount=Decimal('10.00'),
            tax_amount=Decimal('5.00'),
            status='pending',
            payment_status='pending'
        )
        
        # Set up the test client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_payment_process_view(self):
        """Test the payment process view"""
        url = reverse('payment:process', args=[self.order.id])
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/process.html')
        
        # Test POST request with valid payment method
        response = self.client.post(url, {'payment_method': 'credit_card'})
        self.assertEqual(response.status_code, 302)  # Should redirect after successful payment
        
        # Verify order status updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'processing')
    
    def test_payment_completed_view(self):
        """Test the payment completed view"""
        url = reverse('payment:completed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/completed.html')
