from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva, Pixel, UserAction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.utils.timezone import now
from datetime import timedelta


def home(request):
    context = {'canvases': Canva.objects.all().order_by('-save_count')}
    return render(request, 'blog/home.html', context)

class CanvaListView(ListView):
    model = Canva
    template_name = 'blog/home.html'
    context_object_name = 'canvases'
    ordering = ['-save_count']

class CanvaDetailView(DetailView):
    model = Canva

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pixels = self.object.pixels.all()
        grid = [[None for _ in range(self.object.sizeWidth)] for _ in range(self.object.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel
        context['pixels'] = grid

        # Calcul du temps restant pour l'utilisateur
        user_action = UserAction.objects.filter(user=self.request.user, canva=self.object).first()
        if user_action:
            time_since_last_action = now() - user_action.last_modified
            time_remaining = max(0, self.object.timer - time_since_last_action.seconds)
            context['time_remaining'] = time_remaining
        else:
            context['time_remaining'] = 0

        return context



@login_required
def update_pixel(request, pk):
    canva = get_object_or_404(Canva, pk=pk)
    user_action, created = UserAction.objects.get_or_create(user=request.user, canva=canva)

    # Récupérer la grille de pixels
    pixels = canva.pixels.all()
    grid = [[None for _ in range(canva.sizeWidth)] for _ in range(canva.sizeHeight)]
    for pixel in pixels:
        grid[pixel.y][pixel.x] = pixel

    if request.method == "POST":
        try:
            x = int(request.POST.get('x'))
            y = int(request.POST.get('y'))
            color = request.POST.get('color')

            # Vérification si les coordonnées sont valides
            if x < 0 or x >= canva.sizeWidth or y < 0 or y >= canva.sizeHeight:
                raise ValueError("Invalid coordinates: outside the canvas bounds.")

            pixel = get_object_or_404(Pixel, canva=canva, x=x, y=y)
            pixel.color = color
            pixel.save()

            canva.save_count += 1
            canva.save()
            user_action.save()

            return HttpResponseRedirect(reverse('canva-detail', args=[pk]))

        except ValueError as e:
            # En cas d'erreur (coordonnées invalides), afficher un message d'erreur
            context = {
                'message': str(e),
                'canva': canva,
                'pixels': grid  # Inclure la grille dans le contexte
            }
            return render(request, 'blog/canva_detail.html', context)


class CanvaCreateView(LoginRequiredMixin, CreateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']
    template_name = 'blog/canva_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialisation de la grille de pixels avec des valeurs par défaut
        size_width = self.request.POST.get('sizeWidth', 5)
        size_height = self.request.POST.get('sizeHeight', 5)

        # Créer une grille de pixels par défaut
        context['pixels'] = [[{'x': x, 'y': y, 'color': '#FFFFFF'} for x in range(int(size_width))] for y in
                             range(int(size_height))]

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Une fois que le canvas est créé, gérer les pixels
        if self.object:
            size_width = form.cleaned_data['sizeWidth']
            size_height = form.cleaned_data['sizeHeight']

            # Récupérer les couleurs des pixels envoyées par le formulaire
            pixel_data = json.loads(self.request.POST.get('pixel_data', '[]'))

            # Mettre à jour ou créer les pixels
            for pixel in pixel_data:
                x = pixel['x']
                y = pixel['y']
                color = pixel['color']

                # Créer un pixel dans la base de données
                Pixel.objects.update_or_create(
                    canva=self.object,
                    x=x,
                    y=y,
                    defaults={'color': color}
                )

        return response


class CanvaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        canva = self.get_object()
        return self.request.user == canva.author

class CanvaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Canva
    success_url = '/'

    def test_func(self):
        canva = self.get_object()
        return self.request.user == canva.author

def statistic(request):
    return render(request, 'blog/statistic.html', {'title': 'statistic'})