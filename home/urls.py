from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

app_name = 'home'
uuid_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

urlpatterns = [
    url(r'^graph', views.graph),
    url(r'^test_send', views.test_send),
]
