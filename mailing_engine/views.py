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

from django.core.mail import EmailMessage
from django.core.mail import send_mail

# Create your views here.

@login_required
def send_info(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id in event.participants.all():
        # send_mail(str(i)+" "+event.name, 'to jest ta rzecz :)', event.owner.first_name, ['kasperski.dominik@gmail.com'], fail_silently=False)
        subject = 'Information about' + event.name
        body = "Dear " + request.user.first_name + "!\n"\
         + "There are requested informations:\n" 
        "What:\t" + event.name + ".\n" +\
        "When:\t" + str(event.date) + ".\n" +\
        "Enrollment begin at \t" + str(event.enrollment_begin) +".\n"\
        "Enrollment finish at \t" + str(event.enrollment_end) +".\n"\
        "Where:\t" + str(event.location) + ".\n"
        if event.price>0:
        	body = body + "Price:\t" + str(event.price) + ".\n"
        body = body + "Additional information:\n" + event.description + "\n" +\
        "Link to an event in COSINE:\t" + request.get_full_path() + "\n" +\
        "Owner's email address:\t" + event.owner.email + "\n" +\
        "Thank You for using our application!"

        message = EmailMessage(subject, body, from_email=event.owner.email, bcc=[user.email, 'kasperski.dominik@gmail.com'])
        message.send()
    if request.user.id == event.owner.id:
        subject = event.name + ' ' + 'information'
        from_email = event.owner.email
        bcc = event.participants.all()
        print(bcc)
        message = EmailMessage('hello', 'test', from_email=event.owner.first_name, bcc=['kasperski.dominik@gmail.com'])
        message.send()
        return render(request, 'mailing_engine/send_info.html', {'event': event,'user':event.owner})
    return HttpResponseForbidden("Only owner can send email with information to all participants!")

def send_info_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id in event.participants.all():
        subject = 'Information about' + event.name
        body = "Dear " + request.user.first_name + "!\n"\
         + "There are requested informations:\n" 
        "What:\t" + event.name + ".\n" +\
        "When:\t" + str(event.date) + ".\n" +\
        "Enrollment begin at \t" + str(event.enrollment_begin) +".\n"\
        "Enrollment finish at \t" + str(event.enrollment_end) +".\n"\
        "Where:\t" + str(event.location) + ".\n"
        if event.price>0:
        	body = body + "Price:\t" + str(event.price) + ".\n"
        body = body + "Additional information:\n" + event.description + "\n" +\
        "Link to an event in COSINE:\t" + request.get_full_path() + "\n" +\
        "Owner's email address:\t" + event.owner.email + "\n" +\
        "Thank You for using our application!"

        message = EmailMessage(subject, body, from_email=event.owner.email, bcc=[user.email, 'kasperski.dominik@gmail.com'])
        message.send()
        return render(request, 'mailing_engine/send_info_participant.html', {'event': event,'user':user})
    return HttpResponseForbidden("Only enrolled one can ask for email with information!")