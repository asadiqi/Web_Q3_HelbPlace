from django.contrib import admin
from .models import Canva # Importing the Post model from the models.py file
from blog.models import PixelModification

admin.site.register(Canva) # Registering the Post model in the admin panel to allow users to manage and view the posts.
admin.site.register(PixelModification)



