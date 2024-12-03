import json
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva,Pixel
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

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
        pixels = self.object.pixels.all()
        grid = [[None for _ in range(self.object.sizeWidth)] for _ in range(self.object.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel
        context['pixels'] = grid
        context['canva'] = self.object  # Assure-toi que 'canva' est passé au template
        return context



class CanvaCreateView(LoginRequiredMixin, CreateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']   
    template_name = 'blog/canva_form.html'
    #success_url = reverse_lazy('blog-home')  # Redirection après création
   
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
