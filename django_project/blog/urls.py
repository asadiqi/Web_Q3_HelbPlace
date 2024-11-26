from django.urls import path # Importing the path function from django.urls module
from .views import PostListView, PostDetailView, PostCreateView,PostUpdateView, PostDeleteView # Importing the PostListView , PostDetailview, PostCreateView class from the views module for ListView, DetailView,CreateView, UpdateView,DeleteView
from . import views # Importing the views module from the current directory

urlpatterns = [
    path('',PostListView.as_view(), name='blog-home'), # 2 Creating a URL pattern for the home page that map us to the home function in the views module
    path('post/<int:pk>/',PostDetailView.as_view(), name='post-detail'), # this pattern maps to the post_detail function in the views module with the post id as a parameter
    path('post/new/',PostCreateView.as_view(), name='post-create'), # this pattern maps to the post_create function in the views module with the post id as a parameter
    path('post/<int:pk>/update/',PostUpdateView.as_view(), name='post-update'), # this pattern maps to the post_update function in the views module with the post id as a parameter
    path('post/<int:pk>/delete/',PostDeleteView.as_view(), name='post-delete'), # this pattern maps to the post_delete function in the views module with the post id as a parameter
    path('about/', views.about, name='blog-about'),
]
 