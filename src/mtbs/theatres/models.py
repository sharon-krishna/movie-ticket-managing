from django.db import models
from movies.models import Movie


class Theatre(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Screen(models.Model):
    theatre = models.ForeignKey(Theatre,on_delete=models.CASCADE,related_name='screens')
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.theatre.name} - {self.name}"


class Seat(models.Model):
    SEAT_TYPE_CHOICES = (
        ('REGULAR', 'Regular'),
        ('PREMIUM', 'Premium'),
    )

    screen = models.ForeignKey(Screen,on_delete=models.CASCADE,related_name='seats')
    row_label = models.CharField(max_length=5)
    seat_number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=20,choices=SEAT_TYPE_CHOICES,default='REGULAR')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('screen', 'row_label', 'seat_number')

    def __str__(self):
        return f"{self.screen.name} {self.row_label}{self.seat_number}"

class Show(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='shows')
    screen = models.ForeignKey(Screen,on_delete=models.CASCADE,related_name='shows')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} @ {self.start_time}"
