from django.contrib.auth.models import User
from django import forms
from cosine.models import Event
from django.contrib.admin.widgets import AdminDateWidget
import datetime



class MessageForm(forms.Form):
    subject = forms.CharField()
    body = forms.CharField()

    class Meta:
        help_texts = {'body': None}
        fields = ['subject','body']
            
        

class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        help_texts = {'body': None}
        fields = ['subject','message']