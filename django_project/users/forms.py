# We can use this form in our view insted of  usercreation form
from django import forms # importing the forms module from Django
from django.contrib.auth.models import User # importing the User model from Django's built-in authentication app
from django.contrib.auth.forms import UserCreationForm # importing the built-in UserCreationForm from Django's built-in authentication app
from . models import Profile # importing the Profile model
class USERRegisterForm(UserCreationForm): # creating a custom form inheriting from UserCreationForm
    email = forms.EmailField() # adding an email field to the form with required=True to ensure that the email is filled out
    
    
    class Meta: # defining the meta class for the form
        model = User # specifying the model to be User
        fields = ['username', 'email', 'password1', 'password2'] # specifying the fields to be included in the form 
        
class UserUpdateForm(forms.ModelForm): # creating a custom form inheriting from ModelForm
     email = forms.EmailField() 
    
     class Meta: 
        model = User 
        fields = ['username', 'email'] # allows as to update username and email 

class ProfileUpdateForm(forms.ModelForm): #allow us to update profile picture
    class Meta:
        model = Profile
        fields = ['image'] # specifying the fields to be included in the form
    