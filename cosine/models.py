from django.db import models
from django.conf import settings
from django.utils import timezone
from django_google_maps import fields as map_fields

class Location(models.Model):
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=100)

    def __str__(self):
        return self.address

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    spots = models.IntegerField()
    image = models.FileField(default='default.png')
    location = models.ForeignKey('Location', on_delete=models.CASCADE)# CharField(max_length=200)
    price = models.FloatField()
    enrollment_begin = models.DateTimeField()
    enrollment_end = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)

    @property
    def can_enroll(self):
        if self.enrollment_end > timezone.now() > self.enrollment_begin and self.participants.count() < self.spots:
            return True
        return False
