from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva, Pixel
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy



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
        return context

@login_required
def update_pixel(request, pk):
    canva = get_object_or_404(Canva, pk=pk)
    if request.method == "POST":
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        color = request.POST.get('color')
        pixel = get_object_or_404(Pixel, canva=canva, x=x, y=y)
        pixel.color = color
        pixel.save()

        # Incrémentation du compteur save_count
        canva.save_count += 1
        canva.save()

        return HttpResponseRedirect(reverse('canva-detail', args=[pk]))


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
