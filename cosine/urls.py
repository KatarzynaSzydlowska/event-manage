from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^event/(?P<event_id>[0-9]+)/$', views.detail, name="detail"),
    url(r'^event/(?P<event_id>[0-9]+)/enroll$', views.enroll, name="enroll"),
    url(r'^event/(?P<event_id>[0-9]+)/leave$', views.leave, name="leave"),
    url(r'^event/(?P<event_id>[0-9]+)/delete$', views.delete, name="delete"),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^logout-then-login/$', auth_views.logout_then_login, name='logout_then_login'),
    url(r'^add-event/$', views.add_event, name='add_event'),
    url(r'^event/(?P<event_id>[0-9]+)/edit-event/$', views.edit_event, name='edit_event'),
    url(r'^event/(?P<event_id>[0-9]+)/$', views.send_info, name='send_info'),
    url(r'^event-list/owned$', views.event_list_owned, name='event_list_owned'),
    url(r'^event-list/enrolled', views.event_list_enrolled, name='event_list_enrolled'),
    url(r'^event-list/available$', views.event_list_available, name='event_list_available'),
    url(r'^$', views.dashboard, name='dashboard'),
]
