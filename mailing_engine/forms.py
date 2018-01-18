from django.contrib.auth.models import User
from django import forms
from cosine.models import Event
from django.contrib.admin.widgets import AdminDateWidget
import datetime


class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)