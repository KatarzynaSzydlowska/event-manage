from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^event/(?P<event_id>[0-9]+)/$', views.send_info, name='send_info'),
]