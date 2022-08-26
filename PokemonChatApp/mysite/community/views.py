
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import FriendRequests, Friends, User
from django.db.models import Q


@login_required(login_url="login")
def community(request):
    # allows user to choose whether to view their inbox or add friends
    try:
        choice = request.session["community_choice"]
    except:
        choice = "inbox"
    
    if request.method == "GET":
        if request.GET.get("view_choice") == "inbox":
            choice = "inbox"
            request.session["community_choice"] = choice
            
        elif request.GET.get("view_choice") == "friend_request":
            choice = "friend_request"
            request.session["community_choice"] = choice
            
    try:
        # loads in all friends
        friend_group = Friends.objects.get(current_user=request.user)
        friends = friend_group.users.all()
        
    except:
        friends = []
    
    try:
        # loads in different data and features depending on the users choice
        if choice == "inbox":
            friend_requests = FriendRequests.objects.filter(receiver=request.user)
            
            if request.method == "POST":
                if request.POST.get("request_choice")[0:6] == "accept":
                        
                    try:
                        # loads in all neccessary data
                        friend_request = FriendRequests.objects.get(id=request.POST.get("request_choice")[6:])
                        user1 = request.user
                        user2 = User.objects.get(id=friend_request.sender.id)  
            
                        # checks to see if users are already friends
                        exists = Friends.objects.get(current_user=request.user1, users=user2.id) | Friends.objects.get(current_user=user2, users=user1.id)
                        messages.error(request, "Already friends with this user.")
                        return redirect("community")

                    except:
                        print(user1, user2)
                        Friends.make_friend(user1, user2)
                        Friends.make_friend(user2, user1)
                        
                        friend_request.delete()
                        messages.success(request, "Friend added successfully.")
                        return redirect("community")
                
                elif request.POST.get("request_choice")[0:6] == "reject":
                    return redirect("delete-friend-request", id=request.POST.get("request_choice")[6:])
                
            context = {"friends": friends, "choice": choice, "friend_requests": friend_requests}
        
        
        elif choice == "friend_request":
            # loads in all current friend requests
            receivers = FriendRequests.objects.filter(sender=request.user).values("receiver_id")
            senders = FriendRequests.objects.filter(receiver=request.user).values("sender_id")
            
            q = request.GET.get("q") if request.GET.get("q") != None else ""
            
            # filters search input by entered letters
            users = User.objects.filter(Q(username__icontains=q)).exclude(id=request.user.id).exclude(id__in=friends).exclude(id__in=receivers).exclude(id__in=senders)
            user_count = users.count()
            
            if request.method == "POST":
                current_user = request.user
                recieving_user = User.objects.get(id=request.POST.get("friend_request"))
                
                # checks to see if users are already friends
                try:
                    exists = Friends.objects.get(current_user=current_user, users=recieving_user)
                    messages.error(request, "Already friends with this user.")
                    return redirect("community")
                
                except:
                    # sends friend request
                    friend_request = FriendRequests(sender=current_user, receiver=recieving_user)
                    friend_request.save()
                        
                    messages.success(request, "Friend request sent successfully.")
                    return redirect("community")

            context = {"friends": friends, "choice": choice, "users": users, "user_count": user_count}

        return render(request, "community/community.html", context)
    
    except:
        messages.error(request, "Error occured.")
    
    
@login_required(login_url="login")
def deleteFriendRequest(request, id):
    try:
        friend_request = FriendRequests.objects.get(id=id)
        procedure = "reject"

        # checks to see if user has permission
        if request.user.id != friend_request.receiver_id:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("community")
        else:
            if request.method == "POST":
                friend_request.delete()
                
                messages.success(request, "Successfully rejected friend request.")
                return redirect("community")
            
            context = {"obj": "this friend request", "procedure": procedure}
            return render(request, "main/delete.html", context)
    except:
        messages.error(request, "No friend request with this id.")
        return redirect("community") 


@login_required(login_url="login")
def deleteFriend(request, id):
    try:
        friend_object = User.objects.get(id=id)
        friend = Friends.objects.get(current_user=friend_object)
        
        users_friends = friend.users.all()
        procedure = "delete"

        # checks to see if user has permission
        if request.user not in users_friends:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("community")
        else:
            if request.method == "POST":
                Friends.lose_friend(request.user, friend_object)
                Friends.lose_friend(friend_object, request.user)
                
                messages.success(request, "Successfully removed friend.")
                return redirect("community")
            
            context = {"obj": friend_object, "procedure": procedure}
            return render(request, "main/delete.html", context)
    except:
        messages.error(request, "No friend with this id.")
        return redirect("community") 
