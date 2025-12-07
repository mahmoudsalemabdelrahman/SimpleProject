from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'city', 'phone', 'birth_date', 'image')


class UserRegistrationForm(UserCreationForm):
    """Registration form that includes email (required) and validates uniqueness."""
    email = forms.EmailField(required=True, label='البريد الإلكتروني')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email
