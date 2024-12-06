from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Canva, Pixel, PixelModification, UserAction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.db.models.functions import TruncDate
from django.db.models import Count

def home(request):
    canvases = Canva.objects.annotate(
        total_modifications=Sum('useraction__modification_count')
    ).order_by('-total_modifications')

    return render(request, 'blog/home.html', {'canvases': canvases})

class CanvaListView(ListView):
    model = Canva
    template_name = 'blog/home.html'
    context_object_name = 'canvases'


class CanvaDetailView(DetailView):
    model = Canva

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canva = self.object
        pixels = canva.pixels.all()
        grid = [[None for _ in range(canva.sizeWidth)] for _ in range(canva.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel

        user_action = UserAction.objects.filter(user=self.request.user, canva=canva).first()
        if user_action:
            time_since_last_action = now() - user_action.last_modified
            context['time_remaining'] = max(0, canva.timer - time_since_last_action.seconds)
        else:
            context['time_remaining'] = 0

        context['pixels'] = grid
        return context


@login_required
def update_pixel(request, pk):
    canva = get_object_or_404(Canva, pk=pk)
    user_action, created = UserAction.objects.get_or_create(user=request.user, canva=canva)

    grid = [[None for _ in range(canva.sizeWidth)] for _ in range(canva.sizeHeight)]
    for pixel in canva.pixels.all():
        grid[pixel.y][pixel.x] = pixel

    time_since_last_action = now() - user_action.last_modified
    if created or time_since_last_action >= timedelta(seconds=canva.timer):
        if request.method == "POST":
            try:
                x, y = int(request.POST.get('x')), int(request.POST.get('y'))
                color = request.POST.get('color')

                if not (0 <= x < canva.sizeWidth and 0 <= y < canva.sizeHeight):
                    raise ValueError("Invalid coordinates.")

                pixel = get_object_or_404(Pixel, canva=canva, x=x, y=y)
                pixel.color = color
                pixel.save()
                PixelModification.objects.create(pixel=pixel)

                canva.save()
                user_action.last_modified = now()
                user_action.modification_count += 1
                user_action.save()

                return HttpResponseRedirect(reverse('canva-detail', args=[pk]))

            except ValueError as e:
                return render(request, 'blog/canva_detail.html', {
                    'message': str(e),
                    'canva': canva,
                    'pixels': grid
                })
    else:
        time_remaining = (timedelta(seconds=canva.timer) - time_since_last_action).seconds
        return render(request, 'blog/canva_detail.html', {
            'message': f'Please wait {time_remaining} seconds before modifying again.',
            'canva': canva,
            'pixels': grid
        })


class CanvaCreateView(LoginRequiredMixin, CreateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']
    template_name = 'blog/canva_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        size_width = int(self.request.POST.get('sizeWidth', 5))
        size_height = int(self.request.POST.get('sizeHeight', 5))

        context['pixels'] = [[{'x': x, 'y': y, 'color': '#FFFFFF'} for x in range(size_width)] for y in
                             range(size_height)]
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        pixel_data = json.loads(self.request.POST.get('pixel_data', '[]'))
        for pixel in pixel_data:
            Pixel.objects.update_or_create(
                canva=self.object,
                x=pixel['x'],
                y=pixel['y'],
                defaults={'color': pixel['color']}
            )

        return response


class CanvaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author


class CanvaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Canva
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author

def statistic(request):
    canva_id = request.GET.get('canva_id')
    canva = get_object_or_404(Canva, id=canva_id) if canva_id else None


    if canva:
        user_rankings = UserAction.objects.filter(canva=canva) \
        .values('user__username', 'user__id') \
        .annotate(modification_count=Sum('modification_count')) \
        .order_by('-modification_count')


        total_modifications = UserAction.objects.filter(canva=canva).aggregate(total=Sum('modification_count'))['total'] or 0

        # Date de création du Canva jusqu'à aujourd'hui
        start_date = canva.date_posted.date()  # Date de création du canva
        end_date = now().date()  # Date actuelle

        # Liste de toutes les dates entre la date de création et la date actuelle
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Regrouper les modifications par date
        pixel_modifications_by_date = PixelModification.objects.filter(pixel__canva=canva) \
            .annotate(date=TruncDate('modified_at')) \
            .values('date') \
            .annotate(total_modifications=Count('id')) \
            .order_by('date')

        # Transformer la liste de modifications par date en un dictionnaire
        modification_dict = {mod['date']: mod['total_modifications'] for mod in pixel_modifications_by_date}

        # Construire une liste des modifications, en ajoutant 0 pour les dates sans modifications
        pixel_modifications_with_all_dates = []
        for date in date_range:
            pixel_modifications_with_all_dates.append({
                'date': date,
                'total_modifications': modification_dict.get(date, 0)  # 0 si aucune modification
            })

        return render(request, 'blog/statistic.html', {
            'canva': canva,
            'user_rankings': user_rankings,
            'total_modifications': total_modifications,
            'pixel_modifications_by_date': pixel_modifications_with_all_dates,  # Utiliser la nouvelle liste
        })

    return render(request, 'blog/statistic.html', {'canva': canva})

def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Récupérer les canvas où l'utilisateur a participé et leur modification count
    canvas_participation = UserAction.objects.filter(user=user) \
        .values('canva__title', 'canva__id') \
        .annotate(total_modifications=Sum('modification_count')) \
        .order_by('-total_modifications')
    
    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'canvas_participation': canvas_participation,
    })




