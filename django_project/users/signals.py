from django.db.models.signals import post_save # this line is for handling post_save signal
from django.contrib.auth.models import User # this line is for importing User model from django.contrib.auth.models module
from django.dispatch import receiver # this line is for registering receiver function and  we create a recerver that get the signal ans preform some action when it is received
from .models import Profile # this line is for importing Profile model from users.models module


@receiver(post_save, sender=User) # this line is for registering the receiver function to the post_save signal
def create_profile(sender, instance, created, **kwargs): # this function will be called when a new user is created
    if created: # if the user is created
        Profile.objects.create(user=instance) # create a new Profile object with the user 
        
        
        
        
#this is the function to save the profile when a user is saved        
@receiver(post_save, sender=User) 
def save_profile(sender, instance, **kwargs): 
    instance.profile.save() # save the profile when a user is saved
        
# we muste import this signal in our apps.py file to make it work        
        