from django.contrib import admin

from blog.models import PixelModification
from .models import Profile

admin.site.register(Profile)
admin.site.register(PixelModification)


