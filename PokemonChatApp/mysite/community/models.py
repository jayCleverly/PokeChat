from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Friends(models.Model):
    current_user=models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE, null=True)
    users=models.ManyToManyField(User, related_name="users", blank=True)

    @classmethod
    def make_friend(cls,current_user,new_friend):
        friend,create=cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        friend, create = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(new_friend)


class FriendRequests(models.Model):
    sender = models.ForeignKey(User, null=True, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
