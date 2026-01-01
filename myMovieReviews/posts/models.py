# posts/models.py
from django.db import models

class Review(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.CharField(max_length=30)
    rating = models.FloatField()

    director = models.CharField(max_length=50)
    actor = models.CharField(max_length=100)
    running_time = models.IntegerField()
    content = models.TextField()

    def __str__(self):
        return self.title
