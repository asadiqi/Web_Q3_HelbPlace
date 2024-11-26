from django.shortcuts import render # Importing the render function from django.shortcuts module for opening the HTML templates like home.html and about.html
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Importing the LoginRequiredMixin and UserPassesMixin class from django.contrib.auth.mixins module for requiring a user to be logged in to access certain views and have permission to update or delete posts (be the author).
from django.views.generic import ListView, DetailView, CreateView , UpdateView, DeleteView # Importing the ListView DetailView and CreatView class from django.views.generic module for creating list views, detail views, create views,update views, and delete views
from .models import Post # Importing the Post model from the models.py file

# This function will handle HTTP GET requests to the home URL
def home(request):
    context = { # Creating a dictionary with key 'posts' and value as the list of posts. This dictionary will be passed to the home.html template.
        'posts': Post.objects.all() # Passing the posts list to the home.html templat list of dictionaries contians information of eache post  
                       # post well be accessed in the home.html template.
    }
    return render (request,'blog/home.html',context)#3  Returning an HTTP response with the HTML content


class PostListView(ListView): # Creating a class-based view that inherits from ListView
    model = Post # The model we want to list
    template_name = 'blog/home.html' # The name of the template we want to use for this view
    context_object_name = 'posts' # The name of the context variable in the template that will contain the list of objects
    ordering =['-date_posted'] # Ordering the posts by newest to oldest
    
    
class PostDetailView(DetailView):  # Creating a class-based view that inherits from DetailView
    model = Post

   
class PostCreateView(LoginRequiredMixin, CreateView):  # Creating a class-based view that inherits from DetailView and LoginRequiredMixin is for requiring a user to be logged in first then creating a new post
    model = Post
    fields = ['title', 'content']
    
    def form_valid(self, form): # Form validation
        form.instance.author = self.request.user # Setting the author of the post to the currently logged-in user
        return super().form_valid(form) # Calling the form_valid method from the parent class to handle form validation and saving the post to the database
     
   
       
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin,  UpdateView):   # Creating a class-based view that inherits from DetailView, LoginRequiredMixin, UserPassesTestMixin is for requiring a user to be logged in first and have permission to update the post 
    model = Post
    fields = ['title', 'content']
    
    def form_valid(self, form): 
        form.instance.author = self.request.user 
        return super().form_valid(form) 
    def test_func(self): # This method is used to check if the user has permission to create a new post
        post = self.get_object()
        if self.request.user == post.author: # Checking if the user is the author of the post
            return True
        return False
    
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  # Creating a class-based view that inherits from DeleteView
    model = Post
    success_url = '/' # Redirecting to the home page after deleting a post
    def test_func(self): # This method is used to check if the user has permission to create a new post
            post = self.get_object()
            if self.request.user == post.author: # Checking if the user is the author of the post
                return True
            return False  
        
       
    
def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

 