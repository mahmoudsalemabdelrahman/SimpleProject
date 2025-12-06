from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Course, Order, Coupon
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class CouponTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=100.00
        )
        
        self.order = Order.objects.create(
            user=self.user,
            course=self.course,
            amount=self.course.price,
            status='pending'
        )
        
        self.coupon = Coupon.objects.create(
            code='SAVE20',
            discount_percentage=20,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=1),
            active=True
        )

    def test_apply_valid_coupon(self):
        url = reverse('apply_coupon')
        data = {'code': 'SAVE20', 'order_id': self.order.id}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['final_price'], 80.0)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.amount, 80.0)
        self.assertEqual(self.order.coupon, self.coupon)
        self.assertEqual(self.order.discount_amount, 20.0)
        
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_apply_invalid_coupon(self):
        url = reverse('apply_coupon')
        data = {'code': 'INVALID', 'order_id': self.order.id}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.amount, 100.0)

    def test_apply_expired_coupon(self):
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_percentage=50,
            valid_from=timezone.now() - timedelta(days=2),
            valid_to=timezone.now() - timedelta(days=1),
            active=True
        )
        
        url = reverse('apply_coupon')
        data = {'code': 'EXPIRED', 'order_id': self.order.id}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.json()['status'], 'error')
