from django.urls import path
from .views import (
    CanvaListView,
    CanvaDetailView,
    CanvaCreateView,
    CanvaUpdateView,
    CanvaDeleteView,
    update_pixel,
    user_profile
)
from . import views


urlpatterns = [
    path('profile/<int:user_id>/', user_profile, name='profile'),
    path('', views.home, name='home'),
    path('', CanvaListView.as_view(), name='blog-home'),
    path('canva/<int:pk>/', CanvaDetailView.as_view(), name='canva-detail'),
    path('canva/new/', CanvaCreateView.as_view(), name='canva-create'),
    path('canva/<int:pk>/update/', CanvaUpdateView.as_view(), name='canva-update'),
    path('canva/<int:pk>/delete/', CanvaDeleteView.as_view(), name='canva-delete'),
    path('statistic/', views.statistic, name='blog-statistic'),
    path('canva/<int:pk>/update-pixel/', views.update_pixel, name='update-pixel'),
    path('helbplace/canva/', views.helbplace_canva, name='helbplace_canva'),

]