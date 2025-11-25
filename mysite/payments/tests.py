from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Payment

User = get_user_model()

class PaymentBasicTest(TestCase):
    """Basic tests for payment functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass', 
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass')
    
    def test_payment_model_creation(self):
        """Test Payment model can be created"""
        payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id='pi_test_12345',
            amount=100.00,
            currency='usd',
            status='created'
        )
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, 100.00)
        self.assertEqual(payment.currency, 'usd')
        self.assertEqual(payment.status, 'created')
    
    def test_checkout_page_requires_login(self):
        """Test checkout page requires authentication"""
        self.client.logout()
        response = self.client.get('/payments/checkout/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_checkout_page_accessible_when_logged_in(self):
        """Test checkout page is accessible for logged-in users"""
        response = self.client.get('/payments/checkout/')
        self.assertEqual(response.status_code, 200)
    
    def test_success_page_accessible(self):
        """Test success page is accessible"""
        response = self.client.get('/payments/success/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Successful')
    
    def test_cancel_page_accessible(self):
        """Test cancel page is accessible"""
        response = self.client.get('/payments/cancel/')
        self.assertEqual(response.status_code, 200)
