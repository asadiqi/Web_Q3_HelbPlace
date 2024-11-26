"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views # this is for login and logout views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'), # 2 when we go to localhost:8000/register/, it will be redirected to register function in user_views.py file
    path('profile/', user_views.profile, name='profile'), 
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'), #this is for login view
    path('logout/', user_views.logout_view, name='logout'),  # tilisation of logout view personalized in user_views.py file
    path('', include('blog.urls')) # 1  when we open our page in browser and go to localhost:8000/blog/, it will be redirected to blog/urls.py file
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # this line allows to serve media files from the media directory in debug mode.  It should be removed in a production environment.
