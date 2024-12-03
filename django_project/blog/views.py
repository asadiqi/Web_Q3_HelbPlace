from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva, JoinedCanva,Pixel
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

def home(request):
    context = {
        'canvases': Canva.objects.all()
    }
    return render(request, 'blog/home.html', context)

class CanvaListView(ListView):
    model = Canva
    template_name = 'blog/home.html'
    context_object_name = 'canvases'
    ordering = ['-date_posted']
    
    
class CanvaDetailView(DetailView):
    model = Canva

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        canva = self.object

        # Vérifier si l'utilisateur a rejoint ou s'il est l'auteur
        context['joined'] = canva.joined_users.filter(id=user.id).exists() if user.is_authenticated else False
        context['is_author'] = canva.author == user

        # Génération de la grille
        pixels = self.object.pixels.all()
        grid = [[None for _ in range(self.object.sizeWidth)] for _ in range(self.object.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel
        context['pixels'] = grid
        return context




def join_canva(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        canva = get_object_or_404(Canva, pk=pk)

        # Vérifie que l'utilisateur n'est pas l'auteur
        if canva.author != request.user:
            # Ajoute l'utilisateur à la liste des utilisateurs ayant rejoint
            canva.joined_users.add(request.user)

        # Redirige vers la page du Canva
        return redirect('canva-detail', pk=pk)
    return redirect('blog-home')  # Redirige vers la page d'accueil si non authentifié ou GET




@login_required
def update_pixel(request, pk):
    canva = get_object_or_404(Canva, pk=pk)
    user_canva = JoinedCanva.objects.get(user=request.user, canva=canva)
    
    # Vérifier si l'utilisateur a respecté son temps de délai
    if user_canva.last_modified:
        time_since_last_change = timezone.now() - user_canva.last_modified
        if time_since_last_change.total_seconds() < canva.timer:
            remaining_time = canva.timer - time_since_last_change.total_seconds()
            # Afficher un pop-up avec le temps restant
            return JsonResponse({
                'message': f"Vous devez attendre encore {remaining_time:.0f} secondes avant de modifier.",
                'remaining_time': remaining_time
            })
    
    if request.method == "POST":
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        color = request.POST.get('color')

        # Vérifier si le pixel existe et appartient au Canva
        pixel = get_object_or_404(Pixel, canva=canva, x=x, y=y)
        
        # Mettre à jour la couleur
        pixel.color = color
        pixel.save()

        # Mettre à jour le temps de modification de l'utilisateur
        user_canva.last_modified = timezone.now()
        user_canva.save()

        # Rediriger vers la page du Canva
        return HttpResponseRedirect(reverse('canva-detail', args=[pk]))







class CanvaCreateView(LoginRequiredMixin, CreateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']   
    template_name = 'blog/canva_form.html'
    success_url = reverse_lazy('blog-home')  # Redirection après création
   
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class CanvaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Canva
    fields = ['title', 'sizeHeight' , 'sizeWidth', 'timer']  

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        canva = self.get_object()
        if self.request.user == canva.author:
            return True
        return False

class CanvaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Canva
    success_url = '/'

    def test_func(self):
        canva = self.get_object()
        if self.request.user == canva.author:
            return True
        return False

def statistic(request):
    return render(request, 'blog/statistic.html', {'title': 'statistic'})
