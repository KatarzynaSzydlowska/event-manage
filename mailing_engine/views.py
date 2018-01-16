from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from cosine.models import Event
from .forms import ContactForm

import mailing_engine

from django.core.mail import EmailMessage
from django.core.mail import send_mail

# Create your views here.

@login_required
def send_info(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user in event.participants.all():

        msubject = event.name + ' ' + 'information'
        from_email = event.owner.email
        subject = 'Information about ' + event.name
        mbody = "Dear " + request.user.first_name + "! \n "\
        + "There are requested informations: \n " +\
        "What:\t" + event.name + ". \n " +\
        "When:\t" + str(event.date) + ". \n " +\
        "Enrollment begin at \t" + str(event.enrollment_begin) + ". \n " +\
        "Enrollment finish at \t" + str(event.enrollment_end) + ". \n " +\
        "Where:\t" + str(event.location) + " .\n "
        if event.price>0:
            mbody = mbody + "Price:\t" + str(event.price) + ". \n "
        mbody = mbody + "Additional information: \n " + event.description + " \n " +\
        "Link to an event in COSINE:\t" + 'http://event-manage-pite.herokuapp.com/event/'+str(event.id) + " \n " +\
        "Owner's email address:\t" + event.owner.email + " \n " +\
        "Thank You for using COSINE!"
        message = EmailMessage(subject=msubject, body=mbody, from_email=event.owner.email, bcc=[request.user.email])
        message.attach("QR.png", event.qr_code.file.file.read())
        message.send()
        return render(request, 'mailing_engine/send_info.html', {'event': event,'user':request.user})

    if request.user.id == event.owner.id:
        msubject = event.name + ' ' + 'information'
        from_email = event.owner.email
        bcc_participants = [part.email for part in event.participants.all()]
        subject = 'Information about ' + event.name
        mbody = "Dear " + request.user.first_name + "! \n "\
        + "There are requested informations: \n " +\
        "What:\t" + event.name + ". \n " +\
        "When:\t" + str(event.date) + ". \n " +\
        "Enrollment begin at \t" + str(event.enrollment_begin) + ". \n " +\
        "Enrollment finish at \t" + str(event.enrollment_end) + ". \n " +\
        "Where:\t" + str(event.location) + " .\n "
        if event.price>0:
            mbody = mbody + "Price:\t" + str(event.price) + ". \n "
        mbody = mbody + "Additional information: \n " + event.description + " \n " +\
        "Link to an event in COSINE:\t" + 'http://event-manage-pite.herokuapp.com/event/'+str(event.id) + " \n " +\
        "Owner's email address:\t" + event.owner.email + " \n " +\
        "Thank You for using COSINE!"
        message = EmailMessage(subject=msubject, body=mbody, from_email=event.owner.email, bcc=bcc_participants)
        message.attach("QR.png", event.qr_code.file.file.read())
        message.send()
        return render(request, 'mailing_engine/send_info.html', {'event': event,'user':request.user})
    return HttpResponseForbidden("Only owner can send email with information to all participants!")

@login_required
def send_message(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.id == event.owner.id:
        if request.method == 'POST':
            form = ContactForm()
        else:
            form = ContactForm(request.POST)
            if form.is_valid():
                msubject = form.cleaned_data['subject']
                mbody = form.cleaned_data['message']
                bcc_participants = [part.email for part in event.participants.all()]
                mbody = mbody + \
                "Link to an event in COSINE:\t" +\
                 'http://event-manage-pite.herokuapp.com/event/'+str(event.id) + " \n " +\
                "Owner's email address:\t" + event.owner.email + " \n " +\
                "Thank You for using COSINE"
                print(type(mbody))
                message = EmailMessage(subject=msubject, body=mbody, from_email=event.owner.email, bcc=bcc_participants)
                message.attach("QR.png", event.qr_code.file.file.read())
                message.send()                
                return redirect(request, 'mailing_engine/send_info.html', {'event': event,'user':request.user})
        return render(request, 'mailing_engine/send_message.html', {'mail_form': form})
