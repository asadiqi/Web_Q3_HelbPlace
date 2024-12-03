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
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Appeler la méthode save de la classe parente
        
        img = Image.open(self.image.path)  # Ouvrir l'image actuelle
        
        if img.height > 300 or img.width > 300:  # Vérifier les dimensions de l'image
            output_size = (300, 300)
            img.thumbnail(output_size)  # Redimensionner l'image
            img.save(self.image.path)  # Sauvegarder l'image redimensionnée
