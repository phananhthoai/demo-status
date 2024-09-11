
from django.contrib import admin

from .models import Server, State, Alert

admin.site.register(Server)
admin.site.register(State)
admin.site.register(Alert)


