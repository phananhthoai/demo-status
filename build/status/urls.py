from django.urls import path
from django.views.decorators.csrf import csrf_protect
from .views import server_view
from .views import content
from .views import webhook
from .views import webhook_view

urlpatterns = [
    path("server/", server_view, name="server"),
    path("status/", content, name="status"),
    path("webhook/", webhook, name="webhook"),
    path("result/", webhook_view, name="resutl")
]