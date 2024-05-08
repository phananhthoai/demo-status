from django.urls import path

from .views import server_view
from .views import content

urlpatterns = [
    path("server/", server_view, name="server"),
    path("status/", content, name="status"),
]