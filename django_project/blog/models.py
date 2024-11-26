from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse # Importing the reverse function from django.urls module for creating URL patterns dynamically from django 

class Post(models.Model): # Creating a model for our blog posts
    title = models.CharField(max_length=100) # The title of the post
    content = models.TextField() # The content of the post
    date_posted = models.DateTimeField(default=timezone.now) # The date and time when the post was created..
    author = models.ForeignKey(User,on_delete=models.CASCADE)# The author of the post and if a user is deleted, all their posts will also be deleted
    
    def __str__(self): # The string representation of the object when it's printed in shell or in the admin panel
        return self.title # Returning the title of the post
    
    def get_absolute_url(self): # Creating a URL pattern for each post
        return reverse('post-detail', kwargs={'pk': self.pk}) # Returning the URL pattern with the post's primary key as a keyword argument