from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views
app_name = 'mailing_engine'
urlpatterns = [
    url(r'^event/(?P<event_id>[0-9]+)/send_info$', views.send_info, name='send_info'),
    url(r'^event/(?P<event_id>[0-9]+)/send_info_participant$', views.send_info_participant, name='send_info_participant'),
]