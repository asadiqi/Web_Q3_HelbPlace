from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Canva(models.Model):
    title = models.CharField(max_length=100)
    sizeHeight = models.IntegerField()
    sizeWidth = models.IntegerField()
    timer = models.IntegerField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.pixels.exists():
            for x in range(self.sizeWidth):
                for y in range(self.sizeHeight):
                    Pixel.objects.create(canva=self, x=x, y=y)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('canva-detail', kwargs={'pk': self.pk})


class Pixel(models.Model):
    canva = models.ForeignKey(Canva, on_delete=models.CASCADE, related_name='pixels')
    x = models.IntegerField()
    y = models.IntegerField()
    color = models.CharField(max_length=7, default='#FFFFFF')

    class Meta:
        unique_together = ('canva', 'x', 'y')



class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    canva = models.ForeignKey(Canva, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    modification_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.canva.title}'
