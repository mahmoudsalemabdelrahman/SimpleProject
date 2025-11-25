from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

def user_profile_image_path(instance, filename):
    return f"profile_images/user_{instance.user.id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to=user_profile_image_path, default="default/avatar.png")

    # Email Verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
