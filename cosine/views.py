from .models import Event
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import LoginForm, RegistrationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def detail(request, event_id):
    context = {'event': get_object_or_404(Event, pk=event_id)}
    return render(request, 'cosine/detail.html', context)

def register(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'cosine/register_done.html', {'new_user': new_user})
    else:
        user_form = RegistrationForm()
    return render(request, 'cosine/register.html', {'user_form': user_form})

@login_required
def dashboard(request):
    return render(request, 'cosine/dashboard.html', {'section': 'dashboard'})
