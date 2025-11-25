from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import UserEditForm, ProfileEditForm
from .models import Profile

def logout_view(request):
    logout(request)
    return redirect('post_list')


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
@login_required
def profile_edit(request):
    # إنشاء Profile تلقائي لو مش موجود
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # بعد الحفظ اعمل redirect لصفحة البروفايل
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/profile_edit.html", context)


def register(request):
    # Check registration setting
    try:
        # Import here to avoid circular import if any
        from blog.models import SiteSetting
        settings = SiteSetting.objects.first()
        allow_registration = settings.allow_registration if settings else True
    except:
        allow_registration = True

    if not allow_registration:
        return render(request, 'accounts/registration_closed.html')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            user.save()
            
            # Create profile with verification token
            import uuid
            token = uuid.uuid4().hex
            profile, created = Profile.objects.get_or_create(user=user)
            profile.email_verification_token = token
            profile.save()
            
            # Send verification email
            from django.core.mail import send_mail
            from django.urls import reverse
            verification_link = request.build_absolute_uri(
                reverse('verify_email', args=[token])
            )
            
            send_mail(
                subject='تفعيل حسابك - مدونتي',
                message=f'مرحباً {user.username}،\n\nيرجى تفعيل حسابك من خلال الرابط التالي:\n{verification_link}\n\nشكراً لك!',
                from_email='noreply@mysite.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return render(request, 'accounts/email_verification_sent.html', {'email': user.email})
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    """Verify email and activate account"""
    try:
        profile = Profile.objects.get(email_verification_token=token)
        user = profile.user
        
        # Activate user
        user.is_active = True
        user.save()
        
        # Mark email as verified
        profile.is_email_verified = True
        profile.email_verification_token = ''  # Clear token
        profile.save()
        
        return render(request, 'accounts/email_verified.html', {'user': user})
    except Profile.DoesNotExist:
        return render(request, 'accounts/email_verification_failed.html')

