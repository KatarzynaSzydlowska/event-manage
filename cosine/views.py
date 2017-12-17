from .models import Event
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import LoginForm, RegistrationForm, EventForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.core.mail import send_mail


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


@login_required
def add_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES or None)
        if event_form.is_valid():
            new_event = event_form.save(commit=False)
            if 'image' in request.FILES:
                new_event.image = request.FILES['image']
            new_event.owner = User.objects.get(id=request.user.id)
            new_event.save()
            return redirect('detail', event_id=new_event.id)
    else:
        event_form = EventForm()
    return render(request, 'cosine/add_event.html', {'event_form': event_form})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        if request.method == 'POST':
            event_form = EventForm(request.POST, request.FILES or None, instance=event)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                if 'image' in request.FILES:
                    event.image = request.FILES['image']
                event.owner = User.objects.get(id=request.user.id)
                event.save()
                return redirect('detail', event_id=event.id)
        else:
            event_form = EventForm(instance=event)
        return render(request, 'cosine/edit_event.html', {'event_form': event_form})
    return HttpResponseForbidden("Only owner can edit an event!")


@login_required
def detail(request, event_id):
    context = {'event': get_object_or_404(Event, pk=event_id)}
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        return render(request, 'cosine/owner_detail.html', context)
    elif request.user in event.participants.all():
        return render(request, 'cosine/user_detail.html', context)
    else:
        return render(request, 'cosine/detail.html', context)


@login_required
def event_list_owned(request):
    context = {'events': Event.objects.filter(owner__id=request.user.id), 'type': 'owned'}
    return render(request, 'cosine/list.html', context)


@login_required
def event_list_enrolled(request):
    context = {'events': Event.objects.filter(participants__id=request.user.id), 'type': 'enrolled'}
    return render(request, 'cosine/list.html', context)


@login_required
def event_list_available(request):
    context = {
        'events': Event.objects.all().exclude(owner__id=request.user.id).exclude(participants__id=request.user.id),
        'type': 'available'}
    return render(request, 'cosine/list.html', context)


@login_required
def enroll(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.participants.add(request.user)
    event.save()
    return redirect('detail', event_id=event_id)


@login_required
def leave(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.participants.remove(request.user)
    event.save()
    return redirect('event_list_enrolled')


@login_required
def delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        event.delete()
        return redirect('event_list_owned')
    else:
        return HttpResponseForbidden("Only owner can delete an event!")

@login_required
def send_info(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        send_mail(
        'information about '+event.name,
        'Good Morning',
        'from@example.com',
        ['kasperski.dominik@gmail.com'],
        fail_silently=False,
        )
        return redirect('detail', event_id=event.id)
    return HttpResponseForbidden("Only owner can send email with information to all participants!")

