
from django.urls import path
from . import views

urlpatterns = [
    # home urls
    path("home/", views.home, name="home"),
    path("view-group/<str:id>/", views.viewGroup, name="view-group"),
    
    path("create-group/", views.createGroup, name="create-group"),
    path("leave-group/<str:id>/", views.leaveGroup, name="leave-group"),
    
    path("update-group/<str:id>/", views.updateGroup, name="update-group"),
    path("add-members/<str:id>/", views.addMembers, name="add-members"),
    path("process-invites/", views.processInvites, name="process-invites"),
    
    path("delete-group/<str:id>/", views.deleteGroup, name="delete-group"),
    path("delete-message/<str:id>/", views.deleteMessage, name="delete-message"),
    path("delete-group-invite/<str:id>/", views.deleteGroupInvite, name="delete-group-invite"),
]
