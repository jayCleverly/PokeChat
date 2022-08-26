from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Group, Topic, Message, User, GroupInvites
from .forms import GroupForm
from django.contrib import messages


@login_required(login_url="login")
def home(request):
    # allows user to choose whether to view their groups or add new ones
    try:
        choice = request.session["home_choice"]
    except:
        choice = "my_groups"
    
    if request.method == "GET":
        if request.GET.get("view_choice") == "my_groups":
            choice = "my_groups"
            request.session["home_choice"] = choice
        elif request.GET.get("view_choice") == "find_groups":
            choice = "find_groups"
            request.session["home_choice"] = choice
    
    # loads in different data and features depending on the users choice
    if choice == "my_groups":
        q = request.GET.get("q") if request.GET.get("q") != None else ""
        # filters search input by entered letters, works for topic or name
        groups = Group.objects.filter(
                                    (Q(topic__name__icontains=q) |  
                                    Q(name__icontains=q)) &
                                    (Q(members=request.user) |
                                    Q(host=request.user))).distinct()
        
        topics = Topic.objects.all()
        context = {"groups": groups, "topics": topics, "choice": choice}
        
    elif choice == "find_groups":
        q = request.GET.get("q") if request.GET.get("q") != None else ""
        # filters search input by entered letters, works for topic or name
        groups = Group.objects.filter((Q(topic__name__icontains=q) |  
                                    Q(name__icontains=q)) &
                                    Q(public=True)).exclude(members=request.user).exclude(host=request.user)
        
        topics = Topic.objects.all()
        group_count = groups.count()
        context = {"groups": groups, "topics": topics, "group_count": group_count, "choice": choice}
    
    return render(request, "main/home.html", context)
        
        
@login_required(login_url="login")
def viewGroup(request, id):
    try:
        group = Group.objects.get(id=id)
        members = group.members.all()
        group_invites = GroupInvites.objects.filter(receiver=request.user, sender=group)
        
        # checks to see if group is allowed to be viewed by current user
        if group.public == False and request.user not in members and request.user != group.host and group_invites.count()==0:
            messages.error(request, "This group is private.")
            return redirect("home")
        else:
            chats = group.message_set.all()
            participant = True
            
            if request.user not in members and request.user != group.host:
                participant = False
                # adds member to group when they click join button
                if request.method == "POST":
                    group.members.add(request.user)
                    
                    if group_invites.count() != 0:
                        group_invites.delete()
                    
                    messages.success(request, "Joined group.")
                    return redirect("view-group", id=group.id)
                
            else:
                # sends message to the group
                if request.method == "POST":
                    message = Message.objects.create(
                        user = request.user,
                        group = group,
                        text = request.POST.get("text")
                    )
                    return redirect("view-group", id=group.id)
                
            context = {"group": group, "group_messages": chats, "members": members, "participant": participant}
            return render(request, "main/view_group.html", context)
    except:
        messages.error(request, "No group with this id.")
        return redirect("home")


@login_required(login_url="login")
def createGroup(request):
    form = GroupForm()
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            # checks to see if group name already exists
            group = form.save(commit=False)
            try:
                existing = Group.objects.get(name=group.name)
                messages.error(request, "Group already exists with this name.")
            
            except:
                # allocates group the host
                group.host = request.user
                group.save()
            
                messages.success(request, "Created group successfully.")
                return redirect("home")
        
    context = {"form": form}
    return render(request, "main/group_form.html", context)
        

@login_required(login_url="login")
def updateGroup(request, id):
    try:
        group = Group.objects.get(id=id)
        form = GroupForm(instance=group)
        
        # checks to see if user has permission
        if request.user != group.host:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("home")
        else:
            if request.method == "POST":
                form = GroupForm(request.POST, instance=group)
                if form.is_valid():
                    form.save()
                    return redirect("home")
            
            context = {"form": form}
            return render(request, "main/group_form.html", context)
    except:
        messages.error(request, "No group with this id.")
        return redirect("home")


@login_required(login_url="login")
def addMembers(request, id):
    try:
        # loads in object and members of object
        group_object = Group.objects.get(id=id)
        members = group_object.members.all()

        # checks to see if user has permission
        if request.user != group_object.host:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("home")
        else:
            # loads in all current invites
            receivers = GroupInvites.objects.filter(sender=group_object).values("receiver_id")
            
            q = request.GET.get("q") if request.GET.get("q") != None else ""
            
            # filters search input by entered letters
            users = User.objects.filter(Q(username__icontains=q)).exclude(id=request.user.id).exclude(id__in=members).exclude(id__in=receivers)
            user_count = users.count()
            
            if request.method == "POST":
                userid = request.POST.get("invite")
                receiver = User.objects.get(id=userid)
                
                g = GroupInvites(sender=group_object, receiver=receiver)
                g.save()
                
                messages.success(request, "Invite sent successfully.")
                return redirect("add-members", id=id)
                
            context = {"group": group_object, "users":users, "user_count": user_count}
            return render(request, "main/add_members.html", context)
    except:
        messages.error(request, "No group with this id.")
        return redirect("home")


@login_required(login_url="login")
def processInvites(request):
    # loads in invites
    group_invites = GroupInvites.objects.filter(receiver=request.user)

    if request.method == "POST":
        if request.POST.get("invite_choice")[0:6] == "accept":
            
            # adds user to the group
            group_invite = GroupInvites.objects.get(id=request.POST.get("invite_choice")[6:])
            group = Group.objects.get(id=group_invite.sender.id)
            group.members.add(request.user)
            
            group.save()
            group_invite.delete()
            
            messages.success(request, "Invite accepted successfully.")
            return redirect("view-group", id=group_invite.sender.id)
                
                
        elif request.POST.get("invite_choice")[0:6] == "reject":
            return redirect("delete-group-invite", id=request.POST.get("invite_choice")[6:])

    context = {"group_invites": group_invites}
    return render(request, "main/process_invites.html", context)


@login_required(login_url="login")
def deleteGroupInvite(request, id):
    try:
        group_invites = GroupInvites.objects.get(id=id)
        procedure = "reject"
        
        # checks to see if user has permission
        if group_invites.receiver == request.user:
            if request.method == "POST":
                group_invites.delete()
                
                messages.success(request, "Successfully reject group invite.")
                return redirect("process-invites")
            
        else:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("process-invites")
        
        context = {"obj": group_invites.sender, "procedure": procedure}
        return render(request, "main/delete.html", context)
    except:
        messages.error(request, "No invite with this id.")
        return redirect("home")
        

@login_required(login_url="login")
def leaveGroup(request, id):
    try:
        group = Group.objects.get(id=id)
        procedure = "leave"
        
        # checks to see if user has permission
        if Group.objects.filter(members=request.user, id=group.id).count() == 0:
            messages.warning(request, "You are not a part of this group.")
            return redirect("home")
        else:
            if request.method == "POST":
                group.members.remove(request.user)
                
                messages.success(request, "Successfully left group.")
                return redirect("home")
            
            return render(request, "main/delete.html", {"obj": group, "procedure": procedure})
    except:
        messages.error(request, "No group with this id.")
        return redirect("home")
        

@login_required(login_url="login")
def deleteGroup(request, id):
    try:
        group = Group.objects.get(id=id)
        procedure = "delete"
        
        # checks to see if user has permission
        if request.user != group.host:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("home")
        else:
            if request.method == "POST":
                group.delete()
                
                messages.success(request, "Successfully deleted group.")
                return redirect("home")
            
            return render(request, "main/delete.html", {"obj": group, "procedure": procedure})
    except:
        messages.error(request, "No group with this id.")
        return redirect("home")


@login_required(login_url="login")
def deleteMessage(request, id):
    try:
        message = Message.objects.get(id=id)
        procedure = "delete"
        
        if request.user != message.user:
            messages.warning(request, "You do not have permissions to do this.")
            return redirect("view-group", id=request.session["groupid"])
        else:
            if request.method == "POST":
                groupid = message.group.id
                message.delete()
                
                return redirect("view-group", id=groupid)
            
            return render(request, "main/delete.html", {"obj": message, "procedure": procedure})
    except:
        messages.error(request, "No message with this id.")
        return redirect("home")
        
