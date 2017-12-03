from django.contrib.auth.models import User
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)    

class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(label = "Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label = "Retype password", widget=forms.PasswordInput)

    class Meta:
        model = User
        help_texts = { 'username': None,}
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match!")
        return cd['password2']
