"""
Django signals for automatic notifications
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Comment, Course, Certificate, QuizAttempt, Enrollment, Notification, Post


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def clear_site_cache(sender, instance, **kwargs):
    """Clear the entire site cache when a post is changed"""
    cache.clear()


@receiver(post_save, sender=Comment)
def notify_comment_reply(sender, instance, created, **kwargs):
    """Notify user when someone replies to their comment"""
    if created and instance.parent:
        # Someone replied to a comment
        parent_comment = instance.parent
        if parent_comment.user != instance.user:  # Don't notify self
            Notification.objects.create(
                user=parent_comment.user,
                notification_type='comment_reply',
                title='رد جديد على تعليقك',
                message=f'{instance.user.username} رد على تعليقك: "{parent_comment.body[:50]}..."',
                link=f'/post/{instance.post.slug}/#comment-{instance.id}'
            )


@receiver(post_save, sender=Course)
def notify_new_course(sender, instance, created, **kwargs):
    """Notify all users when a new course is published"""
    if created:
        from django.contrib.auth.models import User
        # Notify all active users
        users = User.objects.filter(is_active=True).exclude(id=instance.id if hasattr(instance, 'id') else None)
        notifications = [
            Notification(
                user=user,
                notification_type='new_course',
                title='كورس جديد متاح!',
                message=f'تم إضافة كورس جديد: {instance.title}',
                link=f'/courses/{instance.id}/'
            )
            for user in users[:100]  # Limit to first 100 users for performance
        ]
        Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=Certificate)
def notify_certificate_issued(sender, instance, created, **kwargs):
    """Notify user when they receive a certificate"""
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='certificate',
            title='🎉 تهانينا! حصلت على شهادة',
            message=f'تم إصدار شهادة إتمام لكورس: {instance.course.title}',
            link=f'/certificates/download/{instance.certificate_id}/'
        )


@receiver(post_save, sender=QuizAttempt)
def notify_quiz_result(sender, instance, created, **kwargs):
    """Notify user about quiz results"""
    if not created and instance.is_completed and instance.percentage is not None:
        # Quiz was just completed
        status = 'ناجح' if instance.passed else 'راسب'
        Notification.objects.create(
            user=instance.user,
            notification_type='quiz_result',
            title=f'نتيجة الاختبار: {status}',
            message=f'حصلت على {instance.percentage:.1f}% في اختبار "{instance.quiz.title}"',
            link=f'/quiz/results/{instance.id}/'
        )


@receiver(post_save, sender=Enrollment)
def notify_enrollment(sender, instance, created, **kwargs):
    """Notify user when they enroll in a course"""
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='enrollment',
            title='تم التسجيل بنجاح!',
            message=f'تم تسجيلك في كورس: {instance.course.title}',
            link=f'/courses/{instance.course.id}/'
        )
