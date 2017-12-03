from django.test import TestCase
from cosine.models import Event
from django.contrib.auth.models import User
from django.utils import timezone


class TestSetup(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user("user_1")
        self.user_2 = User.objects.create_user("user_2")
        self.event = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10, price=100,
                                     enrollment_begin=timezone.now(), enrollment_end=timezone.now(),
                                     owner=self.user_1)
        self.event.participants.add(self.user_1, self.user_2)
        self.event.save()

    def tearDown(self):
        self.user_1.delete()
        self.user_2.delete()
        self.event.delete()


class EventTestCase(TestSetup):

    def test_filter_events_by_participants_id(self):
        self.assertEqual(self.event, Event.objects.filter(participants__id=self.user_1.id)[0])

    def test_list_participants_of_event(self):
        self.assertEqual(list(self.event.participants.all()), [self.user_1,self.user_2])


class ViewTestCase(TestSetup):

    def test_call_index_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/index.html')

    def test_call_detail_loads(self):
        response = self.client.get('/{}'.format(self.event.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_call_detail_returns_404_for_nonexistent_website(self):
        response = self.client.get('/{}'.format(10000))
        self.assertEqual(response.status_code, 404)
