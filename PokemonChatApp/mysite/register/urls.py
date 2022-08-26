from django.urls import path
from . import views

urlpatterns = [
    # entry page
    path("", views.entry, name="entry"),
    
    # registration urls
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register"),
    path("logout/", views.logout_user, name="logout"),
    
    # profile urls
    path("profile/<str:id>/", views.viewProfile, name="profile"),
    path("update-profile/<str:id>/", views.update_profile, name="update-profile"),
]
