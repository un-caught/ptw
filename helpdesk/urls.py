from django.urls import path
from . import views


app_name = 'helpdesk'
urlpatterns = [
    path('', views.home, name="home"),
]