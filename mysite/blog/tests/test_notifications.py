from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Post, Comment, Notification
import json

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client.force_login(self.user1)
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user1,
            published=True
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user1,
            body='Original Comment'
        )

    def test_comment_reply_notification(self):
        # User 2 replies to User 1's comment
        Comment.objects.create(
            post=self.post,
            user=self.user2,
            body='Reply Comment',
            parent=self.comment
        )
        
        # Check if notification is created for User 1
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.notification_type, 'comment_reply')
        self.assertFalse(notification.is_read)

    def test_get_notifications_api(self):
        # Create a notification manually
        Notification.objects.create(
            user=self.user1,
            notification_type='system',
            title='Test Notification',
            message='Test Message'
        )
        
        url = reverse('get_notifications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['unread_count'], 1)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], 'Test Notification')

    def test_mark_notification_read(self):
        notification = Notification.objects.create(
            user=self.user1,
            notification_type='system',
            title='Test Notification',
            message='Test Message'
        )
        
        url = reverse('mark_notification_read', args=[notification.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
