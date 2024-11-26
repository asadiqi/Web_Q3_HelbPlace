from django.contrib import admin
from .models import Post # Importing the Post model from the models.py file

admin.site.register(Post) # Registering the Post model in the admin panel to allow users to manage and view the posts.



