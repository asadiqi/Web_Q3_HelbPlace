from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import json
from .models import Canva, Pixel, UserAction, PixelModification
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
from django.contrib.auth.models import User

# View for the home page
def home(request):
    canvases = Canva.objects.annotate(
        total_modifications=Sum('useraction__modification_count')
    ).order_by('-total_modifications')

    # Prepare the grid for each canvas
    for canva in canvases:
        pixels = canva.pixels.all()
        grid = [[None for _ in range(canva.sizeWidth)] for _ in range(canva.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel
        canva.grid = grid  # Add grid to the context of each canvas

    return render(request, 'blog/home.html', {'canvases': canvases})

# List view for canvases
class CanvaListView(ListView):
    model = Canva
    template_name = 'blog/home.html'
    context_object_name = 'canvases'

# Detail view for a single canvas
class CanvaDetailView(DetailView):
    model = Canva

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canva = self.object
        pixels = canva.pixels.all()
        grid = [[None for _ in range(canva.sizeWidth)] for _ in range(canva.sizeHeight)]
        for pixel in pixels:
            grid[pixel.y][pixel.x] = pixel

        # Get the last user action for the current user
        user_action = UserAction.objects.filter(user=self.request.user, canva=canva).first()
        if user_action:
            time_since_last_action = now() - user_action.last_modified
            context['time_remaining'] = max(0, canva.timer - time_since_last_action.seconds)
        else:
            context['time_remaining'] = 0

        context['pixels'] = grid
        return context

# Function to update pixel data
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

                # Log the modification
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

# Create view for a new canvas
class CanvaCreateView(LoginRequiredMixin, CreateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']
    template_name = 'blog/canva_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        size_width = int(self.request.POST.get('sizeWidth', 5))
        size_height = int(self.request.POST.get('sizeHeight', 5))

        context['pixels'] = [[{'x': x, 'y': y, 'color': '#FFFFFF'} for x in range(size_width)] for y in range(size_height)]
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Save the pixel data
        pixel_data = json.loads(self.request.POST.get('pixel_data', '[]'))
        for pixel in pixel_data:
            Pixel.objects.update_or_create(
                canva=self.object,
                x=pixel['x'],
                y=pixel['y'],
                defaults={'color': pixel['color']}
            )

        return response

# Update view for an existing canvas
class CanvaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Canva
    fields = ['title', 'sizeHeight', 'sizeWidth', 'timer']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

# Delete view for a canvas
class CanvaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Canva
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object().author

# Statistics view for pixel modifications
def statistic(request):
    canva_id = request.GET.get('canva_id')
    canva = get_object_or_404(Canva, id=canva_id) if canva_id else None

    if canva:
        # User rankings based on modifications
        user_rankings = UserAction.objects.filter(canva=canva) \
            .values('user__username', 'user__id') \
            .annotate(modification_count=Sum('modification_count')) \
            .order_by('-modification_count')

        # Total modifications
        total_modifications = UserAction.objects.filter(canva=canva).aggregate(total=Sum('modification_count'))['total'] or 0

        # Date range for the canvas
        start_date = canva.date_posted.date()
        end_date = now().date()
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Pixel modifications by date
        pixel_modifications_by_date = PixelModification.objects.filter(pixel__canva=canva) \
            .annotate(date=TruncDate('modified_at')) \
            .values('date') \
            .annotate(total_modifications=Count('id')) \
            .order_by('date')

        # Prepare the pixel modification data
        modification_dict = {mod['date']: mod['total_modifications'] for mod in pixel_modifications_by_date}

        pixel_modifications_with_all_dates = []
        for date in date_range:
            pixel_modifications_with_all_dates.append({
                'date': date,
                'total_modifications': modification_dict.get(date, 0)
            })

        # Prepare data for the chart
        dates = [item['date'] for item in pixel_modifications_with_all_dates]
        modifications = [item['total_modifications'] for item in pixel_modifications_with_all_dates]

        # Remove duplicates in dates
        unique_dates = []
        unique_modifications = []
        for i in range(len(dates)):
            if i == 0 or dates[i] != dates[i-1]:
                unique_dates.append(dates[i])
                unique_modifications.append(modifications[i])

        # Generate the plot
        plt.figure(figsize=(10, 5))
        plt.plot(unique_dates, unique_modifications, marker='o', color='b')
        plt.title(f"The evolution of the Canva : {canva.title}", fontsize=16)
        plt.xlabel("Date since graphic was created", fontsize=12)
        plt.ylabel("Total Modifications by day", fontsize=12)
        plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Save the plot in a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        return render(request, 'blog/statistic.html', {
            'canva': canva,
            'user_rankings': user_rankings,
            'total_modifications': total_modifications,
            'pixel_modifications_by_date': pixel_modifications_with_all_dates,
            'chart': image_base64,
        })

    return render(request, 'blog/statistic.html', {'canva': canva})

# User profile view
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_actions = UserAction.objects.filter(user=user).values(
        'canva__title'
    ).annotate(modification_count=Sum('modification_count')).order_by('-modification_count')

    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'user_canva_modifications': user_actions
    })
