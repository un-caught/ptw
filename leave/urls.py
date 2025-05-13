from django.urls import path
from . import views


app_name = 'leave'
urlpatterns = [
    path('', views.home, name="home"),
    path('apply_leave', views.leave_application, name="leave_application"),
    path('history/', views.leave_history, name='leave_history'),
    path('relief-requests/', views.relief_officer, name='relief_leave_list'),

]