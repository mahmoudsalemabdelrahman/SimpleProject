from django.contrib import admin
from .models import (
    Post, Category, Comment, Tag, SiteSetting, ContactMessage,
    Course, Lesson, Video, Enrollment, LessonProgress, Review, 
    Subscriber, Bookmark, Certificate, Quiz, Question, Answer, 
    QuizAttempt, UserAnswer, Notification
)

# ============= Blog Admin =============

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'post_type', 'published', 'created_at', 'views_count')
    list_filter = ('published', 'created_at', 'category', 'post_type', 'author')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ('author',)
    list_editable = ('published', 'category')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'short_body')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'body', 'post__title')
    
    def short_body(self, obj):
        return obj.body[:50]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one setting instance
        if self.model.objects.exists():
            return False
        return True

# ============= Course Admin =============

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'views_count', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'price')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_live', 'created_at')
    list_filter = ('is_live', 'created_at')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')

# ============= Quiz Admin =============

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'question_type', 'points', 'order')
    list_filter = ('quiz', 'question_type')
    inlines = [AnswerInline]

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson', 'quiz_type', 'is_active')
    list_filter = ('course', 'quiz_type', 'is_active')
    inlines = [QuestionInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'start_time', 'is_completed')
    list_filter = ('passed', 'is_completed', 'quiz')
    search_fields = ('user__username', 'quiz__title')

# ============= Other Admin =============

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'user', 'course', 'issue_date', 'grade')
    search_fields = ('certificate_id', 'user__username', 'course__title')
    readonly_fields = ('certificate_id', 'issue_date')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('user__username', 'title', 'message')

admin.site.register(Subscriber)
admin.site.register(Bookmark)
admin.site.register(LessonProgress)
admin.site.register(UserAnswer)


