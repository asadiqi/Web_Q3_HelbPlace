from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva, Pixel, UserAction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
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

            if time_remaining > 0:
                context['message'] = f'Please wait {time_remaining} seconds before modifying again.'
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

    # Vérification du timer
    time_since_last_action = now() - user_action.last_modified
    if time_since_last_action < timedelta(seconds=canva.timer):
        time_remaining = (timedelta(seconds=canva.timer) - time_since_last_action).seconds
        context = {
            'message': f'Please wait {time_remaining} seconds before modifying again.',
            'canva': canva,
            'pixels': grid  # Inclure la grille dans le contexte
        }
        return render(request, 'blog/canva_detail.html', context)

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
    success_url = reverse_lazy('blog-home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

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

