from django.test import TestCase
from cosine.models import Event
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse
from cosine.forms import LoginForm, RegistrationForm, EventForm, CommentForm
from django.core.files.uploadedfile import SimpleUploadedFile
from mailing_engine.forms import ContactForm
import unittest

# Create your tests here.


class TestSetup(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user("test_user", password='12345')
        self.user_2 = User.objects.create_user("test_user_2", password='12345')
        self.user_1.save()
        self.event = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10,
                                          price=100,
                                          enrollment_begin=timezone.now(),
                                          enrollment_end=timezone.now()+ timezone.timedelta(minutes=100),
                                          owner=self.user_1)
        self.event.participants.add(self.user_1, self.user_2)
        self.event.save()
        self.event2 = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10,
                                           price=100,
                                           enrollment_begin=timezone.now(),
                                           enrollment_end=timezone.now() - timezone.timedelta(minutes=100),
                                           owner=self.user_2)
        self.event2.save()
        self.user3 = User.objects.create_user(username='user1',
                                              password='12345',
                                              first_name='Us',
                                              last_name='Er',
                                              email='user@user.com')
        self.user3.save()

    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.event.delete()
        self.event2.delete()
        self.user3.delete()

class FormTest(TestSetup):
    def test_ContactForm(self):
        form = ContactForm(data={'subject': 'subject', 'message': 'message'})
        self.assertTrue(form.is_valid())
        form = ContactForm(data={'subject': '', 'message': 'message'})
        self.assertFalse(form.is_valid())
        form = ContactForm(data={'subject': 'subject', 'message': ''})
        self.assertFalse(form.is_valid())
		
class ViewTestCase(TestSetup):
    @unittest.expectedFailure
    def test_mail_sending_for_event_participant(self):
        self.client.login(username='test_user_2', password='12345')
        response = self.client.get(reverse('mailing_engine:send_info', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'mailing_engine/send_info.html')

    @unittest.expectedFailure
    def test_mail_sending_for_event_owner(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('mailing_engine:send_info', kwargs={'event_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_send_message_for_event_owner(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('mailing_engine:send_message', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)