from django.test import TestCase
from django.urls import reverse
from blog.models import Post, Course, Category
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SitemapTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='Test content',
            published=True,
            category=self.category
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=0
        )

    def test_sitemap(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<?xml', response.content)
        self.assertIn(b'/post/test-post/', response.content)
        self.assertIn(f'/courses/{self.course.pk}/'.encode(), response.content)
