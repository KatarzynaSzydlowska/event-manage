from django.db import models
from django.conf import settings


class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    spots = models.IntegerField()
    image = models.FileField(default='default.png')
    location = models.CharField(max_length=200)  # TODO,  change to some location framework
    price = models.FloatField()
    enrollment_begin = models.DateTimeField()
    enrollment_end = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
