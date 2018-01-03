from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from cosine.forms import LoginForm, RegistrationForm, EventForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from cosine.models import Event


import mailing_engine

# Create your views here.

@login_required
def send_info(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        send_mail('TEST', 'IT WORKS', 'kasperski.dominik@gmail.com', ['kasperski.dominik@gmail.com'], fail_silently=False)
        return redirect('detail', event_id=event.id)
    return HttpResponseForbidden("Only owner can send email with information to all participants!")