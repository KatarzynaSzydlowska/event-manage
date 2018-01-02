from django.contrib import admin
from .models import Event
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields

admin.site.register(Event)

class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
