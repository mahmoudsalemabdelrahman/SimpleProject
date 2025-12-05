from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse
import random
from .models import (
    Post, Category, Comment, Tag, SiteSetting,
    Course, Lesson, Enrollment, LessonProgress, Order,
    Certificate, Quiz, Question, Answer, QuizAttempt, UserAnswer,
    Video, Notification
)
from .forms import (
    PostForm, CommentForm, CategoryForm, ContactForm, SiteSettingForm,
    CourseForm, LessonForm, VideoForm, ReviewForm, SubscriberForm
)
from .certificate_generator import generate_certificate_pdf








def staff_check(user):
    return user.is_staff

def post_list(request):
    # Get settings
    try:
        settings = SiteSetting.objects.first()
        per_page = settings.posts_per_page if settings else 5
    except:
        per_page = 5

    q = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    tag_slug = request.GET.get('tag', '')
    posts = Post.objects.filter(published=True).order_by('-created_at')
    
    # Unified Search: Search Courses too
    from .models import Course
    courses = Course.objects.none()

    if q:
        posts = posts.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(author__username__icontains=q) |
            Q(category__name__icontains=q)
        )
        courses = Course.objects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    paginator = Paginator(posts, per_page)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    categories = Category.objects.all()

    context = {
        'posts': posts,
        'courses': courses,  # Add courses to context
        'categories': categories,
        'q': q,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
    }
    return render(request, 'blog/post_list.html', context)


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', slug=slug)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    
    # Track views using session
    session_key = f'viewed_post_{post.id}'
    if not request.session.get(session_key, False):
        post.views_count += 1
        post.save(update_fields=['views_count'])
        request.session[session_key] = True
    
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')
    
    # Check settings for comments
    try:
        settings = SiteSetting.objects.first()
        allow_comments = settings.allow_comments if settings else True
    except:
        allow_comments = True

    if request.method == "POST" and allow_comments:
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.user = request.user
            new.post = post
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_obj = Comment.objects.get(pk=int(parent_id))
                    new.parent = parent_obj
                except Comment.DoesNotExist:
                    new.parent = None
            new.save()
            return redirect('post_detail', slug=slug)
    else:
        form = CommentForm()
    
    # Get related posts
    related_posts = Post.objects.filter(category=post.category, published=True).exclude(id=post.id)[:3]
    if not related_posts.exists():
        related_posts = Post.objects.filter(published=True).exclude(id=post.id).order_by('-created_at')[:3]
    
    # Check if bookmarked
    is_bookmarked = False
    if request.user.is_authenticated:
        from .models import Bookmark
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'allow_comments': allow_comments,
        'related_posts': related_posts,
        'is_bookmarked': is_bookmarked
    })



@login_required
@user_passes_test(staff_check)
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # التأكد من وجود post_type، وإلا استخدم القيمة الافتراضية
            if not post.post_type:
                post.post_type = 'article'
            
            post.save()
            form.save_m2m()  # حفظ الـ tags والعلاقات الأخرى
            return redirect('post_list')
    else:
        form = PostForm()
    
    category_form = CategoryForm()
    return render(request, 'blog/post_form.html', {'form': form, 'category_form': category_form})



@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_create')  # بعد إنشاء الكاتيجوري يرجع للفورم
    else:
        form = CategoryForm()
    return render(request, 'blog/category_form.html', {'form': form})

@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.author and not request.user.is_staff:
        return redirect('post_detail', slug=slug)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # التأكد من وجود post_type
            if not post.post_type:
                post.post_type = 'article'
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})



@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.author and not request.user.is_staff:
        return redirect('post_detail', slug=slug)

    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user and not request.user.is_staff:
        return redirect('post_detail', slug=comment.post.slug)
    if request.method == "POST":
        comment.delete()
        return redirect('post_detail', slug=comment.post.slug)
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})


# Admin dashboard — only for staff

@user_passes_test(staff_check)
def admin_dashboard(request):
    posts_count = Post.objects.count()
    comments_count = Comment.objects.count()
    users_count = __import__('django.contrib.auth').contrib.auth.get_user_model().objects.count()
    recent_posts = Post.objects.order_by('-created_at')[:5]
    recent_comments = Comment.objects.order_by('-created_at')[:5]
    recent_users = __import__('django.contrib.auth').contrib.auth.get_user_model().objects.order_by('-date_joined')[:5]

    context = {
        'posts_count': posts_count,
        'comments_count': comments_count,
        'users_count': users_count,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'recent_users': recent_users,
    }
    return render(request, 'blog/admin_dashboard.html', context)


@user_passes_test(staff_check)
def manage_users(request):
    User = __import__('django.contrib.auth').contrib.auth.get_user_model()
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        if user_id and action:
            try:
                user = User.objects.get(pk=user_id)
                if action == 'make_staff':
                    user.is_staff = True
                    user.save()
                elif action == 'remove_staff':
                    user.is_staff = False
                    user.save()
            except User.DoesNotExist:
                pass
            return redirect('manage_users')

    return render(request, 'blog/manage_users.html', {'users': users})


@user_passes_test(staff_check)
def site_settings(request):
    setting, created = SiteSetting.objects.get_or_create(id=1)
    if request.method == "POST":
        form = SiteSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('site_settings')
    else:
        form = SiteSettingForm(instance=setting)
    return render(request, 'blog/site_settings.html', {'form': form})





def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'blog/contact.html', {'form': ContactForm(), 'success': True})
    else:
        form = ContactForm()
    return render(request, 'blog/contact.html', {'form': form})

def robots_txt(request):
    """Simple robots.txt serving view."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def news_list(request):
    news = Post.objects.filter(post_type='news', published=True).order_by('-created_at')
    return render(request, 'blog/news_list.html', {'news': news})


def course_list(request):
    from .models import Course
    from django.db.models import Count
    
    courses = Course.objects.all().annotate(enrollment_count=Count('enrollments'))
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        courses = courses.filter(title__icontains=search_query) | courses.filter(description__icontains=search_query)
    
    # Filter by price
    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        courses = courses.filter(price=0)
    elif price_filter == 'paid':
        courses = courses.filter(price__gt=0)
    
    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'popular':
        courses = courses.order_by('-enrollment_count')
    elif sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    else:
        courses = courses.order_by(sort_by)
    
    return render(request, 'blog/course_list.html', {
        'courses': courses,
        'search_query': search_query,
        'price_filter': price_filter,
        'sort_by': sort_by
    })




def course_detail(request, pk):
    from .models import Course, Enrollment, LessonProgress, Review, Bookmark
    from .forms import ReviewForm
    course = get_object_or_404(Course, pk=pk)
    
    # Track views using session
    session_key = f'viewed_course_{course.id}'
    if not request.session.get(session_key, False):
        course.views_count += 1
        course.save(update_fields=['views_count'])
        request.session[session_key] = True
    
    is_enrolled = False
    completed_lessons = []
    user_review = None
    is_bookmarked = False
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        is_bookmarked = Bookmark.objects.filter(user=request.user, course=course).exists()
        
        if is_enrolled:
            completed_lessons = LessonProgress.objects.filter(
                user=request.user, 
                lesson__course=course, 
                is_completed=True
            ).values_list('lesson_id', flat=True)
            
            # Check if user already reviewed
            user_review = Review.objects.filter(user=request.user, course=course).first()
            
            # Handle review submission
            if request.method == "POST" and not user_review:
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.course = course
                    review.save()
                    return redirect('course_detail', pk=pk)
    
    review_form = ReviewForm() if is_enrolled and not user_review else None
    reviews = course.reviews.all().order_by('-created_at')

    return render(request, 'blog/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'completed_lessons': completed_lessons,
        'review_form': review_form,
        'reviews': reviews,
        'user_review': user_review,
        'is_bookmarked': is_bookmarked
    })


def video_list(request):
    from .models import Video
    videos = Video.objects.all().order_by('-created_at')
    live_stream = Video.objects.filter(is_live=True).first()
    return render(request, 'blog/video_list.html', {'videos': videos, 'live_stream': live_stream})


@login_required
@user_passes_test(staff_check)
def course_create(request):
    from .forms import CourseForm
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'blog/course_form.html', {'form': form})


@login_required
@user_passes_test(staff_check)
def lesson_create(request):
    from .forms import LessonForm
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = LessonForm()
    return render(request, 'blog/lesson_form.html', {'form': form})


@login_required
@user_passes_test(staff_check)
def video_create(request):
    from .forms import VideoForm
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('video_list')
    else:
        form = VideoForm()
    return render(request, 'blog/video_form.html', {'form': form})


@login_required
def course_enroll(request, pk):
    from .models import Course, Enrollment, Order
    course = get_object_or_404(Course, pk=pk)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', pk=pk)
    
    # Free Course
    if course.price == 0:
        Enrollment.objects.create(user=request.user, course=course)
        # Create a completed order for record keeping (optional but good for analytics)
        Order.objects.create(
            user=request.user,
            course=course,
            amount=0,
            status='completed'
        )
        return redirect('course_detail', pk=pk)
    
    # Paid Course -> Create Pending Order
    order = Order.objects.create(
        user=request.user,
        course=course,
        amount=course.price,
        status='pending'
    )
    return redirect('checkout', order_id=order.id)


@login_required
def checkout(request, order_id):
    from .models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    return render(request, 'blog/checkout.html', {'order': order})


@login_required
def process_payment(request, order_id):
    """Simulate Payment Processing"""
    from .models import Order, Enrollment
    import time
    
    if request.method != "POST":
        return redirect('checkout', order_id=order_id)
        
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')
    
    # Simulate processing delay
    time.sleep(2)
    
    # Mark as completed
    order.status = 'completed'
    order.save()
    
    # Enroll user
    Enrollment.objects.get_or_create(user=request.user, course=order.course)
    
    return redirect('payment_success', order_id=order.id)


@login_required
def payment_success(request, order_id):
    from .models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user, status='completed')
    return render(request, 'blog/payment_success.html', {'order': order})


@login_required
def mark_lesson_complete(request, pk):
    from .models import Lesson, LessonProgress

    if request.method == "POST":
        lesson = get_object_or_404(Lesson, pk=pk)
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.is_completed = not progress.is_completed # Toggle status
        progress.save()
        return JsonResponse({'status': 'success', 'is_completed': progress.is_completed})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def student_dashboard(request):
    from .models import Enrollment, LessonProgress
    from datetime import datetime, timedelta
    from django.db.models import Count
    
    # 1. Fetch all enrollments with course details (select_related)
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # 2. Fetch ALL completed lessons for this user in ONE query
    completed_lessons_ids = set(
        LessonProgress.objects.filter(user=request.user, is_completed=True)
        .values_list('lesson_id', flat=True)
    )
    
    # 3. Calculate overall statistics
    total_courses = enrollments.count()
    total_completed_lessons = len(completed_lessons_ids)
    
    courses_data = []
    total_lessons_all_courses = 0
    
    for enrollment in enrollments:
        course = enrollment.course
        
        # Calculate progress in memory (No new DB queries)
        total_lessons = course.lessons.count() 
        total_lessons_all_courses += total_lessons
        
        # Count how many of this course's lessons are in the completed set
        course_lesson_ids = set(course.lessons.values_list('id', flat=True))
        completed_count = len(course_lesson_ids.intersection(completed_lessons_ids))
        
        progress = 0
        if total_lessons > 0:
            progress = int((completed_count / total_lessons) * 100)
            
        courses_data.append({
            'course': course,
            'progress': progress,
            'completed_lessons': completed_count,
            'total_lessons': total_lessons
        })
    
    # 4. Calculate overall completion percentage
    overall_progress = 0
    if total_lessons_all_courses > 0:
        overall_progress = int((total_completed_lessons / total_lessons_all_courses) * 100)
    
    # 5. Weekly activity data (last 7 days)
    today = datetime.now().date()
    weekly_activity = []
    weekly_labels = []
    
    for i in range(6, -1, -1):  # Last 7 days
        day = today - timedelta(days=i)
        count = LessonProgress.objects.filter(
            user=request.user,
            is_completed=True,
            completed_at__date=day
        ).count()
        weekly_activity.append(count)
        weekly_labels.append(day.strftime('%a'))  # Mon, Tue, etc.
    
    context = {
        'courses_data': courses_data,
        'total_courses': total_courses,
        'total_completed_lessons': total_completed_lessons,
        'total_lessons': total_lessons_all_courses,
        'overall_progress': overall_progress,
        'weekly_activity': weekly_activity,
        'weekly_labels': weekly_labels,
    }
    
    return render(request, 'blog/student_dashboard.html', context)


def subscribe_newsletter(request):
    from .forms import SubscriberForm

    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'تم الاشتراك بنجاح!'})
        return JsonResponse({'status': 'error', 'message': 'البريد الإلكتروني مسجل مسبقاً.'})
    return JsonResponse({'status': 'error'}, status=400)


def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html')


def sitemap(request):
    # Generate XML sitemap
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{}</loc>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{}</loc>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{}</loc>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{}</loc>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{}</loc>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{}</loc>
        <priority>0.7</priority>
    </url>
</urlset>'''.format(
        request.build_absolute_uri(reverse('post_list')),
        request.build_absolute_uri(reverse('news_list')),
        request.build_absolute_uri(reverse('course_list')),
        request.build_absolute_uri(reverse('video_list')),
        request.build_absolute_uri(reverse('about')),
        request.build_absolute_uri(reverse('contact'))
    )
    
    return HttpResponse(xml_content, content_type='application/xml')


@login_required
def toggle_bookmark(request, content_type, pk):
    from .models import Bookmark

    
    if content_type == 'post':
        post = get_object_or_404(Post, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if not created:
            bookmark.delete()
            return JsonResponse({'status': 'removed', 'message': 'تم إلغاء الحفظ'})
        return JsonResponse({'status': 'added', 'message': 'تم الحفظ بنجاح'})
    elif content_type == 'course':
        course = get_object_or_404(Course, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, course=course)
        if not created:
            bookmark.delete()
            return JsonResponse({'status': 'removed', 'message': 'تم إلغاء الحفظ'})
        return JsonResponse({'status': 'added', 'message': 'تم الحفظ بنجاح'})
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def my_bookmarks(request):
    from .models import Bookmark
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post', 'course').order_by('-created_at')
    return render(request, 'blog/my_bookmarks.html', {'bookmarks': bookmarks})


def custom_404(request, exception):
    return render(request, '404.html', status=404)


# ============= Certificate Views =============
@login_required
def generate_certificate(request, course_id):
    """Generate certificate for completed course"""
    
    course = get_object_or_404(Course, pk=course_id)
    
    # Check if user is enrolled
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        return JsonResponse({'error': 'غير مسجل في هذا الكورس'}, status=403)
    
    # Check if all lessons are completed
    total_lessons = course.lessons.count()
    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        is_completed=True
    ).count()
    
    if total_lessons == 0 or completed_lessons < total_lessons:
        return JsonResponse({'error': 'يجب إكمال جميع الدروس أولاً'}, status=400)
    
    # Check if certificate already exists
    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        return JsonResponse({
            'status': 'success',
            'message': 'تم إنشاء الشهادة بنجاح!',
            'certificate_id': certificate.certificate_id
        })
    else:
        return JsonResponse({
            'status': 'exists',
            'message': 'الشهادة موجودة بالفعل',
            'certificate_id': certificate.certificate_id
        })


@login_required
def download_certificate(request, certificate_id):
    """Download certificate PDF"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    # Check if user owns this certificate
    if certificate.user != request.user:
        return HttpResponse('غير مصرح', status=403)
    
    # Generate PDF
    pdf_buffer = generate_certificate_pdf(certificate, request)
    
    # Return as file response
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate_id}.pdf"'
    return response


def verify_certificate(request, certificate_id):
    """Public certificate verification page"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    return render(request, 'blog/certificate_verify.html', {'certificate': certificate})


@login_required
def my_certificates(request):
    """List user's certificates"""
    certificates = Certificate.objects.filter(user=request.user).select_related('course').order_by('-issue_date')
    return render(request, 'blog/my_certificates.html', {'certificates': certificates})


# ============= Quiz Views =============
@login_required
def quiz_list(request, course_id):
    """List all quizzes for a course"""
    from .models import Course, Quiz, QuizAttempt
    course = get_object_or_404(Course, pk=course_id)
    
    # Check if enrolled
    from .models import Enrollment
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        return redirect('course_detail', pk=course_id)
    
    quizzes = Quiz.objects.filter(course=course, is_active=True).prefetch_related('questions')
    
    # Get user's attempts for each quiz
    quiz_data = []
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-start_time')
        best_attempt = attempts.filter(is_completed=True).order_by('-percentage').first()
        
        quiz_data.append({
            'quiz': quiz,
            'attempts_count': attempts.count(),
            'attempts_left': max(0, quiz.max_attempts - attempts.count()),
            'best_score': best_attempt.percentage if best_attempt else None,
            'passed': best_attempt.passed if best_attempt else False
        })
    
    return render(request, 'blog/quiz_list.html', {
        'course': course,
        'quiz_data': quiz_data
    })


@login_required
def quiz_detail(request, quiz_id):
    """Quiz instructions and start page"""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check if enrolled
    from .models import Enrollment
    is_enrolled = Enrollment.objects.filter(user=request.user, course=quiz.course).exists()
    if not is_enrolled:
        return redirect('course_detail', pk=quiz.course.id)
    
    # Get user's attempts
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-start_time')
    attempts_left = max(0, quiz.max_attempts - attempts.count())
    
    # Get best score
    best_attempt = attempts.filter(is_completed=True).order_by('-percentage').first()
    
    return render(request, 'blog/quiz_detail.html', {
        'quiz': quiz,
        'attempts': attempts,
        'attempts_left': attempts_left,
        'best_attempt': best_attempt
    })


@login_required
def take_quiz(request, quiz_id):
    """Take quiz interface"""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check if enrolled
    from .models import Enrollment
    is_enrolled = Enrollment.objects.filter(user=request.user, course=quiz.course).exists()
    if not is_enrolled:
        return redirect('course_detail', pk=quiz.course.id)
    
    # Check attempts left
    attempts_count = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    if attempts_count >= quiz.max_attempts:
        return redirect('quiz_detail', quiz_id=quiz_id)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        attempt_number=attempts_count + 1
    )
    
    # Get questions
    questions = list(quiz.questions.all().prefetch_related('answers'))
    
    # Randomize if needed
    if quiz.randomize_questions:
        random.shuffle(questions)
    
    return render(request, 'blog/take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'attempt': attempt
    })


@login_required
def submit_quiz(request, attempt_id):
    """Submit quiz and calculate score"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    
    if attempt.is_completed:
        return JsonResponse({'error': 'الاختبار مكتمل بالفعل'}, status=400)
    
    # Mark end time and completion status
    attempt.end_time = timezone.now()
    attempt.is_completed = True
    
    # Process answers
    for question in attempt.quiz.questions.all():
        answer_id = request.POST.get(f'question_{question.id}')
        text_answer = request.POST.get(f'text_{question.id}', '')
        
        if answer_id:
            try:
                selected_answer = Answer.objects.get(pk=int(answer_id), question=question)
                user_answer = UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer,
                    text_answer=text_answer
                )
                user_answer.check_answer()
            except (Answer.DoesNotExist, ValueError):
                # Invalid answer, create empty user answer
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer
                )
        elif text_answer:
            # Short answer question
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                text_answer=text_answer
            )
    
    # Calculate score (this will save the attempt with all data)
    percentage = attempt.calculate_score()
    
    return JsonResponse({
        'status': 'success',
        'percentage': float(percentage),
        'passed': attempt.passed,
        'redirect_url': f'/quiz/results/{attempt_id}/'
    })


@login_required
def quiz_results(request, attempt_id):
    """View quiz results"""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    
    if not attempt.is_completed:
        return redirect('quiz_detail', quiz_id=attempt.quiz.id)
    
    return render(request, 'blog/quiz_results.html', {'attempt': attempt})


@login_required
def quiz_review(request, attempt_id):
    """Review quiz answers"""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    
    if not attempt.is_completed:
        return redirect('quiz_detail', quiz_id=attempt.quiz.id)
    
    if not attempt.quiz.show_answers:
        return redirect('quiz_results', attempt_id=attempt_id)
    
    # Get all questions with user answers
    questions_data = []
    for question in attempt.quiz.questions.all():
        user_answer = attempt.user_answers.filter(question=question).first()
        questions_data.append({
            'question': question,
            'user_answer': user_answer,
            'all_answers': question.answers.all()
        })
    
    return render(request, 'blog/quiz_review.html', {
        'attempt': attempt,
        'questions_data': questions_data
    })


# ============= Notifications Views =============
@login_required
def notifications_list(request):
    """List all notifications for current user"""
    # Get latest 50 notifications
    notifications_qs = Notification.objects.filter(user=request.user)
    # Force evaluation to get the list
    notifications = list(notifications_qs[:50])
    
    # Get IDs of unread notifications in this batch to mark them as read
    unread_ids = [n.id for n in notifications if not n.is_read]
    
    if unread_ids:
        Notification.objects.filter(id__in=unread_ids).update(is_read=True)
        # Update local instances to reflect change in template
        for n in notifications:
            if n.id in unread_ids:
                n.is_read = True
    
    return render(request, 'blog/notifications.html', {'notifications': notifications})


@login_required
def get_unread_count(request):
    """Get unread notifications count (AJAX)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read (AJAX)"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

