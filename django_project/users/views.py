from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import USERRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':  # if the form is submitted
        form = USERRegisterForm(request.POST)  # create a form object from the UserCreationForm class
        if form.is_valid():  # if the form is valid
            form.save()  # save the user
            username = form.cleaned_data.get('username')  # get the username from the cleaned data
            messages.success(request, f'Your account has been created! You are now able to log in.')  # display success message
            return redirect('login')  # redirect to the login page
    else:  # if the form is not submitted
        form = USERRegisterForm()
    return render(request, 'users/register.html', {'form': form})  # render the form in the template


def logout_view(request):
    logout(request)  # logout the user
    return render(request, 'users/logout.html')  # render the logout template


@login_required()  # restrict access to this view to authenticated users
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)  # create a form for updating user info
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)  # form for updating profile picture
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # save updated user information
            p_form.save()  # save updated profile picture
            messages.success(request, 'Your account has been updated!')  # success message
            return redirect('profile')  # redirect to the profile page
    else:
        u_form = UserUpdateForm(instance=request.user)  # create form for updating user info
        p_form = ProfileUpdateForm(instance=request.user.profile)  # form for updating profile picture
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)  # render the profile template
