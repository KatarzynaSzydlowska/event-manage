from django.contrib.auth.models import User
from django import forms
from .models import Event, Comment
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
import datetime


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
    description = forms.CharField(widget=forms.Textarea( attrs={'rows': 3, 'cols': 25}))
    spots = forms.IntegerField()
    location = forms.CharField()  # TODO,  change to some location framework
    price = forms.FloatField()
    enrollment_begin = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'class': 'datetimepicker'}))
    enrollment_end = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'class': 'datetimepicker'}))

    class Meta:
        model = Event
        fields = ['name', 'date', 'image', 'description', 'spots', 'location', 'price', 'enrollment_begin',
                  'enrollment_end']

    def clean_spots(self):
        cd = self.cleaned_data
        if cd['spots']<0:
            raise forms.ValidationError("You need to declare number of spots greater than 0!")
        return cd['spots']

    def clean_price(self):
        cd = self.cleaned_data
        if cd['price']<0:
            raise forms.ValidationError("Price should be at least 0!")
        return cd['price']

    def clean(self):
        cd = self.cleaned_data
        now = timezone.now()
        if cd['date'] < now:
            raise forms.ValidationError("Date should be later than now!")
        if cd['enrollment_begin'] < now:
            raise forms.ValidationError("Enrollment cannot start before now!")
        if cd['enrollment_begin'] > cd['date']:
            raise forms.ValidationError("Enrollment begin date cannot be later than event date!")
        if cd['enrollment_end'] < cd['enrollment_begin']:
            raise forms.ValidationError("Enrollment end date cannot be earlier than enrollment begin date!")
        if cd['enrollment_end'] > cd['date']:
            raise forms.ValidationError("Enrollment end date cannot be later than event date!")

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['body',]
