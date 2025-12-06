from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    Post, Category, Tag, ContactMessage, 
    Course, Lesson, Enrollment, Quiz, Question, Answer, QuizAttempt, Certificate
)

class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.tag = Tag.objects.create(name='Test Tag')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user,
            category=self.category
        )
        self.post.tags.add(self.tag)

    def test_post_has_tag(self):
        self.assertIn(self.tag, self.post.tags.all())

    def test_like_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(f'/post/{self.post.slug}/like/')
        self.assertEqual(response.status_code, 302)  # Redirects
        self.assertEqual(self.post.total_likes(), 1)
        
        # Unlike
        response = self.client.get(f'/post/{self.post.slug}/like/')
        self.assertEqual(self.post.total_likes(), 0)

    def test_post_list_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test Tag')

    def test_about_page_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/about.html')

    def test_contact_page_status_code(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/contact.html')

    def test_contact_form_submission(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())


class CourseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student', password='password')
        self.course = Course.objects.create(title='Python Course', description='Learn Python', price=0)
        self.lesson = Lesson.objects.create(course=self.course, title='Intro', order=1)

    def test_course_list_view(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Course')

    def test_enrollment(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('course_enroll', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_lesson_completion(self):
        self.client.login(username='student', password='password')
        # Enroll first
        Enrollment.objects.create(user=self.user, course=self.course)
        
        response = self.client.post(reverse('mark_lesson_complete', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['is_completed'], True)


class QuizTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student', password='password')
        self.course = Course.objects.create(title='Quiz Course', description='Testing Quizzes')
        Enrollment.objects.create(user=self.user, course=self.course)
        
        self.quiz = Quiz.objects.create(
            title='Test Quiz', 
            course=self.course, 
            pass_percentage=50
        )
        self.question = Question.objects.create(
            quiz=self.quiz, 
            question_text='Is Python great?', 
            points=10
        )
        self.answer_correct = Answer.objects.create(
            question=self.question, 
            answer_text='Yes', 
            is_correct=True
        )
        self.answer_wrong = Answer.objects.create(
            question=self.question, 
            answer_text='No', 
            is_correct=False
        )

    def test_take_quiz(self):
        self.client.login(username='student', password='password')
        
        # Start quiz
        response = self.client.get(reverse('take_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify attempt created
        attempt = QuizAttempt.objects.get(user=self.user, quiz=self.quiz)
        self.assertFalse(attempt.is_completed)

    def test_submit_quiz_pass(self):
        self.client.login(username='student', password='password')
        
        # Create attempt manually to simulate starting
        attempt = QuizAttempt.objects.create(user=self.user, quiz=self.quiz)
        
        # Submit correct answer
        response = self.client.post(reverse('submit_quiz', args=[attempt.id]), {
            f'question_{self.question.id}': self.answer_correct.id
        })
        
        self.assertEqual(response.status_code, 200)
        attempt.refresh_from_db()
        self.assertTrue(attempt.is_completed)
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.score, 10)

    def test_submit_quiz_fail(self):
        self.client.login(username='student', password='password')
        attempt = QuizAttempt.objects.create(user=self.user, quiz=self.quiz)
        
        # Submit wrong answer
        response = self.client.post(reverse('submit_quiz', args=[attempt.id]), {
            f'question_{self.question.id}': self.answer_wrong.id
        })
        
        attempt.refresh_from_db()
        self.assertFalse(attempt.passed)
        self.assertEqual(attempt.score, 0)


class CertificateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='grad', password='password')
        self.course = Course.objects.create(title='Cert Course', description='Get Certified')
        Enrollment.objects.create(user=self.user, course=self.course)
        self.lesson = Lesson.objects.create(course=self.course, title='Final Lesson')

    def test_certificate_generation_success(self):
        self.client.login(username='grad', password='password')
        
        # Complete lesson
        from .models import LessonProgress
        LessonProgress.objects.create(user=self.user, lesson=self.lesson, is_completed=True)
        
        response = self.client.get(reverse('generate_certificate', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Certificate.objects.filter(user=self.user, course=self.course).exists())

    def test_certificate_generation_fail_incomplete(self):
        self.client.login(username='grad', password='password')
        # Lesson NOT completed
        
        response = self.client.get(reverse('generate_certificate', args=[self.course.id]))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Certificate.objects.filter(user=self.user, course=self.course).exists())
