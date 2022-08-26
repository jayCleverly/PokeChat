from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    TEAM_CHOICES = (("Valor", "Valor"),
                    ("Instinct", "Instinct"),
                    ("Mystic", "Mystic"))
    team = models.CharField(max_length=100, choices=TEAM_CHOICES, null=True, blank=True)
    
    trainerCode = models.IntegerField(null=True, blank = True)
    level = models.IntegerField(null=True, blank=True)
    countryOfResidence = models.CharField(max_length=200, null=True, blank=True)
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
