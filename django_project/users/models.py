# we creat profile picture here
from django.db import models
from django.contrib.auth.models import User # importing User model from django.contrib.auth
from PIL import Image # importing Image module from PIL library

# create a model for user profile with image field and one-to-one relationship with User model
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE) # one-to-one relationship with User model and oneToOneField is used to delete theprofile when the user is deleted
    image=models.ImageField(default='default.jpg', upload_to='profile_pics') # image field to store profile picture
    
    def __str__(self):
        return f'{self.user.username} Profile' # string representation of the profile object
    
    
    def save(self):
        super().save() # call the save method of the parent class (models.Model)
        
        img = Image.open(self.image.path) # open the current image 
        
        if img.height > 300 or img.width > 300: # if the  image dimensions are greater than 300
            output_size = (300, 300) # resize the image to 300x300
            img.thumbnail(output_size) # resize the image
            img.save(self.image.path) # save the resized image to the same location as the original image