from django.test import TestCase
from cosine.models import Event
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse
from cosine.forms import LoginForm, RegistrationForm, EventForm, CommentForm
from django.core.files.uploadedfile import SimpleUploadedFile



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


class EventTestCase(TestSetup):
    def test_filter_events_by_participants_id(self):
        self.assertEqual(self.event, Event.objects.filter(participants__id=self.user_1.id)[0])

    def test_list_participants_of_event(self):
        self.assertEqual(list(self.event.participants.all()), [self.user_1, self.user_2])


class ViewTestCase(TestSetup):
    def test_call_detail_loads_if_owner(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('detail', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_call_detail_loads_if_enrolled_user(self):
        self.client.login(username='test_user_2', password='12345')
        response = self.client.get(reverse('detail', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_call_detail_loads_if_not_enrolled_user(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get(reverse('detail', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_call_detail_returns_404_for_nonexistent_website(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get(reverse('detail', kwargs={'event_id': 10000}))
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

    def test_add_event_form_loads_correctly_for_logged_in_user(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get('/add-event', follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_edit_event_form_loads_correctly_for_event_owner(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('edit_event', kwargs={'event_id': 1}), follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_edit_event_form_loads_correctly_for_not_event_owner(self):
        self.client.login(username='test_user_2', password='12345')
        response = self.client.get(reverse('edit_event', kwargs={'event_id': 1}), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_add_event_form_does_not_load_for_unauthorised_user(self):
        response = self.client.get('/add-event', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_add_event_view_if_success(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-12-13 12:12:12',
                                                    'enrollment_end': '2018-12-14 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_add_event_view_if_wrong_date1(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2017-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-12-13 12:12:12',
                                                    'enrollment_end': '2018-12-14 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_wrong_date2(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2017-12-13 12:12:12',
                                                    'enrollment_end': '2018-12-14 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_wrong_date3(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-01-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-01-18 12:12:12',
                                                    'enrollment_end': '2018-01-19 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_wrong_date4(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-12-13 12:12:12',
                                                    'enrollment_end': '2018-12-12 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_wrong_date5(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': '1',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-12-14 12:12:12',
                                                    'enrollment_end': '2018-12-16 13:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_failed(self):
        self.client.login(username='user1', password='12345')

        response = self.client.post('/add-event/', {'name': 'event1',
                                                    'date': '2018-12-15 12:12:12',
                                                    'description': 'test',
                                                    'spots': 'as',
                                                    'location': 'test',
                                                    'price': '12345',
                                                    'enrollment_begin': '2018-12-13 12:12:12',
                                                    'enrollment_end': '2018-12-14 12:12:12',
                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_add_event_view_if_succes_with_pic(self):
        self.client.login(username='user1', password='12345')
        with open('media/default.png', 'rb') as upload_file:
            post_dict = {'name': 'event1',
                         'date': '2018-12-15 12:12:12',
                         'image': SimpleUploadedFile(upload_file.name, upload_file.read()),
                         'description': 'test',
                         'spots': '1',
                         'location': 'test',
                         'price': '12345',
                         'enrollment_begin': '2018-12-13 12:12:12',
                         'enrollment_end': '2018-12-14 12:12:12',
                         }
            response = self.client.post('/add-event/', post_dict, follow=True)
            self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_edit_event_view_if_succes_with_pic(self):
        self.client.login(username='test_user', password='12345')
        with open('media/default.png', 'rb') as upload_file:
            post_dict = {'name': 'event1',
                         'date': '2018-12-15 12:12:12',
                         'image': SimpleUploadedFile(upload_file.name, upload_file.read()),
                         'description': 'test',
                         'spots': '1',
                         'location': 'test',
                         'price': '12345',
                         'enrollment_begin': '2018-12-13 12:12:12',
                         'enrollment_end': '2018-12-14 12:12:12',
                         }
            response = self.client.post('/event/{}/edit-event/'.format(self.event.id), post_dict, follow=True)
            self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_edit_event_view_if_owner(self):
        self.client.login(username='test_user', password='12345')

        response = self.client.post('/event/{}/edit-event/'.format(self.event.id), {'name': 'event1',
                                                                                    'date': '2018-12-15 12:12:12',
                                                                                    'description': 'test',
                                                                                    'spots': '1',
                                                                                    'location': 'test',
                                                                                    'price': '12345',
                                                                                    'enrollment_begin': '2018-12-13 12:12:12',
                                                                                    'enrollment_end': '2018-12-14 12:12:12',
                                                                                    }, follow=True)
        self.assertTemplateUsed(response, 'cosine/detail.html')

    def test_edit_event_view_if_not_owner(self):
        self.client.login(username='test_user_2', password='12345')

        response = self.client.post('/event/1/edit-event/', {'name': 'event1',
                                                             'date': '2018-12-15 12:12:12',
                                                             'description': 'test',
                                                             'spots': '1',
                                                             'location': 'test',
                                                             'price': '12345',
                                                             'enrollment_begin': '2018-12-13 12:12:12',
                                                             'enrollment_end': '2018-12-14 12:12:12',
                                                             }, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_edit_event_view_get_request_if_owner(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get('/event/1/edit-event/', follow=True)
        self.assertTemplateUsed(response, 'cosine/add_edit_event.html')

    def test_edit_event_view_get_request_if_not_owner(self):
        self.client.login(username='test_user_2', password='12345')
        response = self.client.get('/event/1/edit-event/', follow=True)
        self.assertEqual(response.status_code, 403)

    def test_event_list_owned_view(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('event_list_owned'), follow=True)
        self.assertTemplateUsed(response, 'cosine/list.html')
        self.assertEqual(list(response.context['events']), [self.event])

    def test_event_list_available_view(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('event_list_available'), follow=True)
        self.assertTemplateUsed(response, 'cosine/list.html')
        self.assertEqual(list(response.context['events']), [self.event2])

    def test_event_list_enrolled_view(self):
        self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('event_list_enrolled'), follow=True)
        self.assertTemplateUsed(response, 'cosine/list.html')
        self.assertEqual(list(response.context['events']), [self.event])

    def test_enroll_view_when_can(self):
        user = User.objects.create_user("test_user_3", password='12345')
        self.client.login(username='test_user_3', password='12345')
        response = self.client.get(reverse('enroll', kwargs={'event_id': self.event.id}), follow=True)
        self.assertTemplateUsed(response, 'cosine/detail.html')
        self.assertTrue(user in self.event.participants.all())

    def test_enroll_view_when_fail(self):
        user = User.objects.create_user("test_user_3", password='12345')
        self.client.login(username='test_user_3', password='12345')
        response = self.client.get(reverse('enroll', kwargs={'event_id': self.event2.id}), follow=True)
        self.assertTemplateUsed(response, 'cosine/detail.html')
        self.assertTrue(user not in self.event.participants.all())

    def test_leave_view(self):
        user = User.objects.create_user("test_user_3", password='12345')
        self.client.login(username='test_user_3', password='12345')
        self.event.participants.add(user)
        response = self.client.get(reverse('leave', kwargs={'event_id': self.event.id}), follow=True)
        self.assertTemplateUsed(response, 'cosine/list.html')
        self.assertTrue(user not in self.event.participants.all())

    def test_delete_view(self):
        event = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10,
                                     price=100,
                                     enrollment_begin=timezone.now(), enrollment_end=timezone.now(),
                                     owner=self.user_2)
        event.save()
        self.client.login(username='test_user_2', password='12345')
        response = self.client.get(reverse('delete', kwargs={'event_id': event.id}), follow=True)
        self.assertTemplateUsed(response, 'cosine/list.html')
        self.assertTrue(event not in Event.objects.all())

    def test_delete_view_non_owner_cant_delete(self):
        event = Event.objects.create(name="test", date=timezone.now(), description="test event", spots=10,
                                     price=100,
                                     enrollment_begin=timezone.now(), enrollment_end=timezone.now(),
                                     owner=self.user_2)
        event.save()
        self.client.login(username='user1', password='12345')
        response = self.client.post(reverse('delete', kwargs={'event_id': event.id}), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_comment_add(self):
        self.client.login(username='user1', password='12345')
        response = self.client.post('/event/1/', {'body': 'cos tam'})
        self.assertEqual(response.status_code, 302)


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

    def test_event_form_with_file(self):
        upload_file = open('media/default.png', 'rb')
        post_dict = {'name': 'event1',
                     'date': '2018-12-15 12:12:12',
                     'description': 'test',
                     'spots': '1',
                     'location': 'test',
                     'price': '12345',
                     'enrollment_begin': '2018-12-13 12:12:12',
                     'enrollment_end': '2018-12-14 12:12:12',
                     }
        file_dict = {'file': SimpleUploadedFile(upload_file.name, upload_file.read())}
        form = EventForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

    def test_event_form_without_file(self):
        post_dict = {'name': 'event1',
                     'date': '2018-12-15 12:12:12',
                     'description': 'test',
                     'spots': '1',
                     'location': 'test',
                     'price': '12345',
                     'enrollment_begin': '2018-12-13 12:12:12',
                     'enrollment_end': '2018-12-14 12:12:12',
                     }
        form = EventForm(post_dict)
        self.assertTrue(form.is_valid())

    def test_event_form_proper_price(self):
        post_dict = {'name': 'event1',
                     'date': '2018-12-15 12:12:12',
                     'description': 'test',
                     'spots': '1',
                     'location': 'test',
                     'price': '-12345',
                     'enrollment_begin': '2018-12-13 12:12:12',
                     'enrollment_end': '2018-12-14 12:12:12',
                     }
        form = EventForm(post_dict)
        self.assertFalse(form.is_valid())

    def test_event_form_proper_number_of_spots(self):
        post_dict = {'name': 'event1',
                     'date': '2018-12-15 12:12:12',
                     'description': 'test',
                     'spots': '-1',
                     'location': 'test',
                     'price': '12345',
                     'enrollment_begin': '2018-12-13 12:12:12',
                     'enrollment_end': '2018-12-14 12:12:12',
                     }
        form = EventForm(post_dict)
        self.assertFalse(form.is_valid())

    def test_comment_form_while_valid(self):
        comment_dict = {'body': 'cos tam'}
        form = CommentForm(comment_dict)
        self.assertTrue(form.is_valid())

    def test_comment_form_while_not_valid(self):
        comment_dict = {'body': ''}
        form = CommentForm(comment_dict)
        self.assertFalse(form.is_valid())
