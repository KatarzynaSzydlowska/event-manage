from django.db import models
from django.conf import settings
from django.utils import timezone
from django.shortcuts import reverse
import qrcode
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    spots = models.IntegerField()
    image = models.FileField(default='default.png')
    qr_code = models.FileField(upload_to='qrcodes',default='default.png')
    location = models.CharField(max_length=200)  # TODO,  change to some location framework, mailing_engine requires this field to be string-convertable object!
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

    def generate_qrcode(self,url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=0,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image()

        buffer = io.BytesIO()
        img.save(buffer)
        filename = 'events-%s.png' % (self.id)
        filebuffer = InMemoryUploadedFile(
            buffer, None, filename, 'image/png', buffer.seek(0, os.SEEK_END), None)
        self.qr_code.save(filename, filebuffer)

class Comment(models.Model):
	event = models.ForeignKey(Event, related_name='comments')
	name = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="name")
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ('created',)
