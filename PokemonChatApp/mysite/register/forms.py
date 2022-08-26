from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = "__all__"


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["team", "trainerCode", "level", "countryOfResidence"]

