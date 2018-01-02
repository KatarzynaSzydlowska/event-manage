from django.contrib.auth.models import User
from django import forms
from .models import Event
from django.contrib.admin.widgets import AdminDateWidget
import datetime
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Retype password", widget=forms.PasswordInput)

    class Meta:
        model = User
        help_texts = {'username': None, }
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match!")
        return cd['password2']


class EventForm(forms.ModelForm):
    name = forms.CharField()
    date = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'class': 'datetimepicker'}))
    description = forms.CharField(widget=forms.Textarea)
    spots = forms.IntegerField()
    location = forms.CharField(widget=map_widgets)
    price = forms.FloatField()
    enrollment_begin = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'class': 'datetimepicker'}))
    enrollment_end = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'class': 'datetimepicker'}))

    class Meta:
        model = Event
        fields = ['name', 'date', 'image', 'description', 'spots', 'location', 'price', 'enrollment_begin',
                  'enrollment_end']
