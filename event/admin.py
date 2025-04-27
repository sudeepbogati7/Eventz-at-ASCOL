from django.contrib import admin
from event.models import Event
from authentication.models import CustomUser
# Register your models here.
admin.site.register(Event)
admin.site.register(CustomUser)

