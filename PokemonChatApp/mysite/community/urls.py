from django.urls import path
from . import views

urlpatterns = [
    path("community/", views.community, name="community"),
    
    path("delete-friend-request/<str:id>/", views.deleteFriendRequest, name="delete-friend-request"),
    path("delete-friend/<str:id>/", views.deleteFriend, name="delete-friend"),
]
