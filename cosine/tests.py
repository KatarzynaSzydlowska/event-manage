from django.test import TestCase
from cosine.models import Event
from django.contrib.auth.models import User
from django.utils import timezone
from cosine.forms import LoginForm, RegistrationForm


class TestSetup(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user("user_1")
        self.user_2 = User.objects.create_user("user_2")
        self.event = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10,
                                          price=100,
                                          enrollment_begin=timezone.now(), enrollment_end=timezone.now(),
                                          owner=self.user_1)
        self.event.participants.add(self.user_1, self.user_2)
        self.event.save()
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
        self.user3.delete()


class EventTestCase(TestSetup):
    def test_filter_events_by_participants_id(self):
        self.assertEqual(self.event, Event.objects.filter(participants__id=self.user_1.id)[0])

    def test_list_participants_of_event(self):
        self.assertEqual(list(self.event.participants.all()), [self.user_1, self.user_2])


class ViewTestCase(TestSetup):
    def test_call_detail_loads(self):
        response = self.client.get('/{}'.format(self.event.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_call_detail_returns_404_for_nonexistent_website(self):
        response = self.client.get('/{}'.format(10000))
        self.assertEqual(response.status_code, 404)

    def test_dashboard_redirect_if_not_logged_in(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_dashboard_renders_if_logged_in(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/dashboard.html')

    def test_user_login_view_if_not_succes(self):
        self.client.login(username='user1', password='12345')
        self.client.get('/logout')
        response = self.client.post('/login/', {'username': 'user1', 'password': '112345'})
        self.assertContains(response, 'Incorrect username or password')

    def test_user_login_view_if_succes(self):
        self.client.login(username='user1', password='12345')
        self.client.get('/logout')
        response = self.client.post('/login/', {'username': 'user1', 'password': '12345'}, follow=True)
        self.assertTemplateUsed(response, 'cosine/dashboard.html')

    def test_register_view_if_succes(self):
        response = self.client.get('/register', follow=True)
        self.assertTemplateUsed(response, 'cosine/register.html')
        response = self.client.post('/register/', {'username': 'user2',
                                                   'first_name': 'Aaa',
                                                   'last_name': 'Bbb',
                                                   'email': 'aaa@bbb.com',
                                                   'password2': '12345',
                                                   'password': '12345'}, follow=True)
        self.assertTemplateUsed(response, 'cosine/register_done.html')

    def test_register_view_if_not_succes(self):
        # existing user
        response = self.client.post('/register/', {'username': 'user1',
                                                   'first_name': 'Aaa',
                                                   'last_name': 'Bbb',
                                                   'email': 'aaa@bbb.com',
                                                   'password2': '12345',
                                                   'password': '12345'}, follow=True)
        self.assertTemplateUsed(response, 'cosine/register.html')

        # empty field
        response = self.client.post('/register/', {'username': 'user2',
                                                   'first_name': 'Aaa',
                                                   'last_name': 'Bbb',
                                                   'email': '',
                                                   'password2': '12345',
                                                   'password': '12345'}, follow=True)
        self.assertTemplateUsed(response, 'cosine/register.html')

        # passwords don't match
        response = self.client.post('/register/', {'username': 'user2',
                                                   'first_name': 'Aaa',
                                                   'last_name': 'Bbb',
                                                   'email': 'aaa@bbb.com',
                                                   'password2': '12345',
                                                   'password': 'acbce'}, follow=True)
        self.assertTemplateUsed(response, 'cosine/register.html')


class FormTest(TestCase):
    def test_login_form_validation(self):
        form = LoginForm(data={'username': 'aaa', 'password': 'aaa'})
        self.assertTrue(form.is_valid())
        form = LoginForm(data={'username': '', 'password': ''})
        self.assertFalse(form.is_valid())
        form = LoginForm(data={'username': 'aaa', 'password': ''})
        self.assertFalse(form.is_valid())
        form = LoginForm(data={'username': '', 'password': 'bbb'})
        self.assertFalse(form.is_valid())

    def test_registration_form_validation(self):
        # correct data
        form = RegistrationForm(data={'username': 'user2',
                                      'first_name': 'Aaa',
                                      'last_name': 'Bbb',
                                      'email': 'aaa@bbb.com',
                                      'password2': '12345',
                                      'password': '12345'})
        self.assertTrue(form.is_valid())

        # wrong email pattern
        form = RegistrationForm(data={'username': 'user2',
                                      'first_name': 'Aaa',
                                      'last_name': 'Bbb',
                                      'email': 'aaabbb.com',
                                      'password2': '12345',
                                      'password': '12345'})
        self.assertFalse(form.is_valid())

        # empty field
        form = RegistrationForm(data={'username': 'user2',
                                      'first_name': 'Aaa',
                                      'last_name': '',
                                      'email': 'aaa@bbb.com',
                                      'password2': '12345',
                                      'password': '12345'})
        self.assertFalse(form.is_valid())
