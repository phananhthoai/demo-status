
from django.contrib import admin

from .models import Servers, Status, Alert

admin.site.register(Servers)
admin.site.register(Status)
admin.site.register(Alert)