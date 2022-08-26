from django.shortcuts import render, redirect
from .forms import RegisterForm, AuthenticationForm, ProfileForm

from django.contrib.auth.models import User
from main.models import Message
from .models import Profile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout


"""
Entry Page
"""

def entry(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    context = {}
    return render(request, "register/entry.html", context)


"""
Registration page's Content
"""

def login_user(request):
    if request.user.is_authenticated:
        messages.error(request, "Already logged in.")
        return redirect("home")
    else:
        if request.method == "POST":
            form = AuthenticationForm(None, request.POST)
            username = form["username"].value()
            
            # checks to see if user exists
            try:
                user = User.objects.get(username=username)
                    
                # checks to see if the details are correct
                if form.is_valid():
                    login(request, user)
                    messages.success(request, "Logged in successfully.")
                    return redirect("home")
                else:
                    messages.error(request, "Incorrect password.")
                
            except:
                messages.error(request, "No account found with this username.")
        
        form = AuthenticationForm()
        page = "Login"
        context = {"form": form, "page": page}
        return render(request, "register/login_register.html", context)


def register_user(request):
    if request.user.is_authenticated:
        messages.error(request, "Please logout first.")
        return redirect("home")
    else:
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                
                # checks to see if account already exists with username or email
                try:
                    existing = User.objects.get(username=user.username) | User.objects.get(email = user.email)
                    messages.error(request, "Account exists with these details.")
                
                except:
                    user.save()
                    login(request, user)
                    messages.success(request, "Account created successfully.")
                    return redirect("home")

                else:
                    messages.error(request, "Account exists with these details.")
            else:
                messages.error(request, "An error occured during processing.")
            
        form = RegisterForm()
        page = "Register"
        context = {"form": form, "page": page}
        return render(request, "register/login_register.html", context)


def logout_user(request):
    if request.user.is_authenticated:
        messages.success(request, "Logged out successfully.")
        logout(request)
        return redirect("entry")
    else:
        messages.error(request, "Not logged in.")
        return redirect("login")


"""
Profile page's content
"""

@login_required(login_url="login")
def viewProfile(request, id):
    try:
        profile = Profile.objects.get(user_id=id)
        
        user = User.objects.get(id=id)
        user_messages = Message.objects.filter(user=user, group__public=True)[:10]
        
        context = {"details": profile, "activity": user_messages}
        return render(request, "register/profile.html", context)
    except:
        messages.error(request, "No account with this id.")
        return redirect("home")


@login_required(login_url="login")
def update_profile(request, id):
    try:
        profile = Profile.objects.get(user_id=id)
        form = ProfileForm(instance=profile)
        
        if profile.user.username != request.user.username:
            messages.error(request, "You do not have permissions to edit this profile.")
            return redirect("profile", id=profile.id)
        else:
            if request.method == "POST":
                # updates details if form is valid
                form = ProfileForm(request.POST, instance=profile)
                if form.is_valid():        
                    profile.team = form.cleaned_data.get("team")
                    profile.trainerCode = form.cleaned_data.get("trainerCode")
                    profile.level = form.cleaned_data.get("level")
                    profile.countryOfResidence = form.cleaned_data.get("countryOfResidence")
                    
                    profile.save()
                    messages.success(request, "Successfully updated.")
                    return redirect("profile", id=profile.id)
                else:
                    messages.error(request, "An error occured during updating.")
        
            context = {"form": form, "profile": profile}
            return render(request, "register/profile_form.html", context)
    except:
        messages.error(request, "No account with this id.")
        return redirect("home")

