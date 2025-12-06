from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_update, name='post_update'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('category/new/', views.category_create, name='category_create'),

    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    # admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('site-settings/', views.site_settings, name='site_settings'),


    # static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # New Sections
    path('news/', views.news_list, name='news_list'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('videos/', views.video_list, name='video_list'),

    # Management
    path('courses/create/', views.course_create, name='course_create'),
    path('lessons/create/', views.lesson_create, name='lesson_create'),
    path('videos/create/', views.video_create, name='video_create'),

    # Student Features
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('courses/<int:pk>/enroll/', views.course_enroll, name='course_enroll'),
    path('lessons/<int:pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('lessons/<int:lesson_id>/track-time/', views.track_time, name='track_time'),
    
    path('notifications/api/', views.get_notifications, name='get_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Payment System
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('checkout/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('payment/process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    
    # Newsletter
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    
    # SEO & Legal
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    # path('sitemap.xml', views.sitemap, name='sitemap'),  # Removed in favor of django.contrib.sitemaps
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    # Existing URLs continue...
    path('bookmark/<str:content_type>/<int:pk>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Certificates
    path('certificates/', views.my_certificates, name='my_certificates'),
    path('certificates/generate/<int:course_id>/', views.generate_certificate, name='generate_certificate'),
    path('certificates/download/<str:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('certificates/verify/<str:certificate_id>/', views.verify_certificate, name='verify_certificate'),
    
    # Quizzes
    path('courses/<int:course_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/submit/<int:attempt_id>/', views.submit_quiz, name='submit_quiz'),
    path('quiz/results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    path('quiz/review/<int:attempt_id>/', views.quiz_review, name='quiz_review'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/count/', views.get_unread_count, name='get_unread_count'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]


