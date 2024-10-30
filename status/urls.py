from django.urls import path
from django.views.decorators.csrf import csrf_protect
from .views import view
# from .views import content
from .views import webhook
# from .views import webhook_view

urlpatterns = [
    # path("server/", server_view, name="server"),
    path("", view, name="view"),
    # path("status/", content, name="status"),
    path("webhook/", webhook, name="webhook"),

]