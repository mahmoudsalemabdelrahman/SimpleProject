from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from blog.models import Course, Lesson, LessonProgress, CertificateTemplate, Certificate, Enrollment
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class LMSTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=0
        )
        Enrollment.objects.create(user=self.user, course=self.course)
        
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson',
            order=1
        )
        
        self.template = CertificateTemplate.objects.create(
            name='Default Template',
            html_content='<html><body>{{ student_name }}</body></html>',
            is_default=True
        )

    def test_track_time(self):
        url = reverse('track_time', args=[self.lesson.id])
        response = self.client.post(url, {'duration': 30})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        progress = LessonProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.time_spent, 30)
        
        # Track again
        response = self.client.post(url, {'duration': 30})
        progress.refresh_from_db()
        self.assertEqual(progress.time_spent, 60)

    def test_certificate_template_assignment(self):
        self.course.certificate_template = self.template
        self.course.save()
        
        self.assertEqual(self.course.certificate_template, self.template)
        
    def test_generate_certificate_with_template(self):
        # Create completion
        LessonProgress.objects.create(user=self.user, lesson=self.lesson, is_completed=True)
        
        # Generate
        url = reverse('generate_certificate', args=[self.course.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        cert = Certificate.objects.get(user=self.user, course=self.course)
        self.assertIsNotNone(cert.certificate_id)
