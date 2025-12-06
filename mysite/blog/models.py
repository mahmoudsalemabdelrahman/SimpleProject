from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import unicodedata
import re
from autoslug import AutoSlugField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    slug = AutoSlugField(populate_from='title', unique=True, always_update=False, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    POST_TYPE_CHOICES = [
        ('article', 'مقال'),
        ('news', 'خبر'),
    ]
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='article')
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='blog_posts_likes', blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def reading_time(self):
        # Calculate reading time (average 200 words per minute)
        from django.utils.html import strip_tags
        text = strip_tags(self.content)
        word_count = len(text.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


# دالة slugify تقبل العربي + الإنجليزي
def slugify_mixed(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)  # يترك العربي + الإنجليزي
    return re.sub(r'[-\s]+', '-', text).strip('-').lower()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class SiteSetting(models.Model):
    # General
    site_name = models.CharField(max_length=100, default="مدونتي")
    site_description = models.TextField(default="منصة عربية لمشاركة المعرفة والأفكار.")
    site_logo = models.ImageField(upload_to='site_logo/', null=True, blank=True)
    site_favicon = models.ImageField(upload_to='site_favicon/', null=True, blank=True)
    
    # Contact Info
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True)

    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # Features & Settings
    allow_registration = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    posts_per_page = models.IntegerField(default=5)
    
    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSetting.objects.exists():
            return
        super().save(*args, **kwargs)


class Course(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    youtube_url = models.URLField(blank=True, help_text="YouTube URL")
    is_live = models.BooleanField(default=False, help_text="Check this if this is a Live Stream")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}/5)"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.content_object}"


# ============= Certificate System =============
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=50, unique=True, editable=False)
    issue_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-issue_date']
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.certificate_id})"


# ============= Quiz/Exam System =============
class Quiz(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('lesson', 'اختبار درس'),
        ('course', 'امتحان نهائي'),
    ]
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='quizzes')
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPE_CHOICES, default='lesson')
    description = models.TextField(blank=True)
    pass_percentage = models.IntegerField(default=70, help_text="النسبة المئوية للنجاح")
    time_limit = models.IntegerField(null=True, blank=True, help_text="الوقت بالدقائق (اختياري)")
    max_attempts = models.IntegerField(default=3, help_text="عدد المحاولات المسموحة")
    show_answers = models.BooleanField(default=True, help_text="عرض الإجابات الصحيحة بعد الانتهاء")
    randomize_questions = models.BooleanField(default=False, help_text="ترتيب الأسئلة عشوائياً")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'lesson', 'created_at']
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    def total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'اختيار من متعدد'),
        ('true_false', 'صح/خطأ'),
        ('short_answer', 'إجابة قصيرة'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    question_text = models.TextField()
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    explanation = models.TextField(blank=True, help_text="شرح الإجابة الصحيحة")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['quiz', 'order', 'created_at']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['question', 'order']
    
    def __str__(self):
        correct = "✓" if self.is_correct else "✗"
        return f"{correct} {self.answer_text[:50]}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def process_submission(self, data):
        if self.is_completed:
            return False
            
        from django.utils import timezone
        self.end_time = timezone.now()
        self.is_completed = True
        
        # We need to import UserAnswer here or use string reference if it was a ForeignKey, 
        # but since we are creating objects, we need the class.
        # Since UserAnswer is defined BELOW, we can't use it directly if this method runs at module level (it doesn't).
        # But we can use it inside method.
        # However, to be safe and avoid circular/not-defined issues if moved, we can use apps.get_model or just assume it's there.
        # Given it's the same file, it's fine.
        
        for question in self.quiz.questions.all():
            answer_id = data.get(f'question_{question.id}')
            text_answer = data.get(f'text_{question.id}', '')
            
            if answer_id:
                try:
                    selected_answer = Answer.objects.get(pk=int(answer_id), question=question)
                    user_answer = UserAnswer.objects.create(
                        attempt=self,
                        question=question,
                        selected_answer=selected_answer,
                        text_answer=text_answer
                    )
                    user_answer.check_answer()
                except (Answer.DoesNotExist, ValueError):
                    UserAnswer.objects.create(
                        attempt=self,
                        question=question,
                        text_answer=text_answer
                    )
            elif text_answer:
                UserAnswer.objects.create(
                    attempt=self,
                    question=question,
                    text_answer=text_answer
                )
        
        self.calculate_score()
        return True

    def calculate_score(self):
        total_points = self.quiz.total_points()
        if total_points == 0:
            return 0
        earned_points = sum(ua.points_earned for ua in self.user_answers.all())
        self.score = earned_points
        self.percentage = (earned_points / total_points) * 100
        self.passed = self.percentage >= self.quiz.pass_percentage
        self.save()
        return self.percentage


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)  # For short answer questions
    is_correct = models.BooleanField(default=False)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.question_text[:30]}"
    
    def check_answer(self):
        if self.question.question_type in ['mcq', 'true_false']:
            if self.selected_answer and self.selected_answer.is_correct:
                self.is_correct = True
                self.points_earned = self.question.points
            else:
                self.is_correct = False
                self.points_earned = 0
        # Short answer questions need manual grading
        self.save()
        return self.is_correct


# ============= Notifications System =============
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment_reply', 'رد على تعليق'),
        ('new_course', 'كورس جديد'),
        ('course_update', 'تحديث كورس'),
        ('certificate', 'شهادة جديدة'),
        ('quiz_result', 'نتيجة اختبار'),
        ('enrollment', 'تسجيل في كورس'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

# ============= Payment System =============
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='orders')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    
    # Stripe-specific fields
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

