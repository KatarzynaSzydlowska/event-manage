from .models import Event
from django.shortcuts import render, get_object_or_404


def index(request):
    context = {'all_events': Event.objects.all()}
    return render(request, 'cosine/index.html', context)


def detail(request, event_id):
    context = {'event': get_object_or_404(Event, pk=event_id)}
    return render(request, 'cosine/detail.html', context)
