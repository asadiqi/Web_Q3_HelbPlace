from django.shortcuts import render, redirect
from django.contrib import messages

from blog.models import UserAction
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


@login_required()  # Restreindre l'accès à cette vue aux utilisateurs authentifiés
def profile(request):
    print("testttt")
    # Récupérer les actions de l'utilisateur sur les canvases
    user_actions = UserAction.objects.filter(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)  # Formulaire pour la mise à jour des informations utilisateur
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)  # Formulaire pour la mise à jour de l'image de profil
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # Sauvegarder les informations utilisateur mises à jour
            p_form.save()  # Sauvegarder l'image de profil mise à jour
            messages.success(request, 'Your account has been updated!')  # Message de succès
            return redirect('profile')  # Rediriger vers la page de profil
    else:
        u_form = UserUpdateForm(instance=request.user)  # Créer un formulaire pour mettre à jour les infos utilisateur
        p_form = ProfileUpdateForm(instance=request.user.profile)  # Formulaire pour mettre à jour l'image de profil

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_actions': user_actions  # Ajouter les actions de l'utilisateur sur les canvases
    }
    return render(request, 'users/profile.html', context)  # Rendre le template du profil
